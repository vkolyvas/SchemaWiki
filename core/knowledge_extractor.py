"""Knowledge extraction from code and documentation."""

import re
from pathlib import Path
from typing import Optional

import yaml

from storage.file_store import FileStore


class KnowledgeExtractor:
    """Extract structured knowledge from code and documentation."""

    def __init__(self, file_store: Optional[FileStore] = None):
        """Initialize knowledge extractor."""
        self.file_store = file_store or FileStore()

    def extract_from_python(self, code: str) -> dict:
        """Extract API routes, imports, and other patterns from Python code."""
        results = {
            "imports": [],
            "api_routes": [],
            "function_definitions": [],
            "class_definitions": [],
            "database_models": [],
        }

        # Extract imports
        import_pattern = r"^(?:from\s+(\S+)\s+import\s+(.+)|import\s+(\S+))"
        for match in re.finditer(import_pattern, code, re.MULTILINE):
            if match.group(1):
                results["imports"].append(
                    {
                        "module": match.group(1),
                        "items": match.group(2).split(", "),
                    }
                )
            elif match.group(3):
                results["imports"].append(
                    {
                        "module": match.group(3),
                        "items": [],
                    }
                )

        # Extract API routes
        route_patterns = [
            r"@(?:app|router)\.(get|post|put|patch|delete|options|head)\([\"']([^\"']+)[\"']",
            r"@(?:app|router)\.(get|post|put|patch|delete|options|head)\([\"']([^\"']+)[\"'].*?def\s+(\w+)",
        ]
        for pattern in route_patterns:
            for match in re.finditer(pattern, code):
                method = match.group(1)
                path = match.group(2)
                handler = match.group(3) if match.lastindex >= 3 else "anonymous"
                results["api_routes"].append(
                    {
                        "method": method.upper(),
                        "path": path,
                        "handler": handler,
                    }
                )

        # Extract function definitions
        func_pattern = r"^(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)"
        for match in re.finditer(func_pattern, code, re.MULTILINE):
            results["function_definitions"].append(
                {
                    "name": match.group(1),
                    "params": match.group(2).strip(),
                }
            )

        # Extract class definitions
        class_pattern = r"^class\s+(\w+)(?:\(([^)]+)\))?:"
        for match in re.finditer(class_pattern, code, re.MULTILINE):
            results["class_definitions"].append(
                {
                    "name": match.group(1),
                    "base_classes": match.group(2).split(", ") if match.group(2) else [],
                }
            )

        # Detect SQLAlchemy models
        model_pattern = r"class\s+(\w+)\(.*(?:Base|Model).*\):"
        for match in re.finditer(model_pattern, code):
            results["database_models"].append(match.group(1))

        return results

    def extract_from_yaml(self, yaml_content: str) -> dict:
        """Extract information from YAML files."""
        try:
            data = yaml.safe_load(yaml_content)
            return {"parsed": True, "data": data}
        except yaml.YAMLError:
            return {"parsed": False, "error": "Invalid YAML"}

    def extract_tests_info(self, tests_content: str) -> dict:
        """Extract test coverage information from tests.md."""
        results = {
            "test_files": [],
            "test_functions": [],
            "coverage_percentage": None,
            "test_categories": [],
        }

        # Extract test file references
        file_pattern = r"[\w/]+\.test\.py|[\w/]+_test\.py|[\w/]+/test_[\w/]+\.py"
        results["test_files"] = re.findall(file_pattern, tests_content)

        # Extract test function names
        test_func_pattern = r"def\s+(test_\w+)\s*\(|async\s+def\s+(test_\w+)\s*\("
        for match in re.finditer(test_func_pattern, tests_content):
            results["test_functions"].append(match.group(1) or match.group(2))

        # Extract coverage percentage
        coverage_pattern = r"(\d+)%\s+coverage"
        coverage_match = re.search(coverage_pattern, tests_content)
        if coverage_match:
            results["coverage_percentage"] = int(coverage_match.group(1))

        # Extract test categories
        category_keywords = ["unit", "integration", "e2e", "end-to-end", "functional", "acceptance"]
        for keyword in category_keywords:
            if keyword.lower() in tests_content.lower():
                results["test_categories"].append(keyword)

        return results

    def update_architecture_doc(
        self,
        feature_name: str,
        extracted_knowledge: dict,
    ) -> None:
        """Update architecture.md with extracted knowledge."""
        existing = self.file_store.read_file(feature_name, FileStore.ARCHITECTURE_FILE) or ""

        # Build new content
        new_content = existing.strip()

        if extracted_knowledge.get("api_routes"):
            new_content += "\n\n## API Routes\n\n"
            for route in extracted_knowledge["api_routes"]:
                new_content += f"- `{route['method']} {route['path']}` -> {route['handler']}\n"

        if extracted_knowledge.get("database_models"):
            new_content += "\n\n## Database Models\n\n"
            for model in extracted_knowledge["database_models"]:
                new_content += f"- {model}\n"

        if extracted_knowledge.get("imports"):
            new_content += "\n\n## Key Dependencies\n\n"
            for imp in extracted_knowledge["imports"][:10]:  # Limit to first 10
                new_content += f"- {imp['module']}\n"

        self.file_store.write_file(feature_name, FileStore.ARCHITECTURE_FILE, new_content)

    def update_api_contracts(
        self,
        feature_name: str,
        extracted_knowledge: dict,
    ) -> None:
        """Update api_contracts.yaml with extracted routes."""
        contracts = {
            "routes": [],
            "models": [],
        }

        if extracted_knowledge.get("api_routes"):
            for route in extracted_knowledge["api_routes"]:
                contracts["routes"].append(
                    {
                        "method": route["method"],
                        "path": route["path"],
                        "handler": route["handler"],
                    }
                )

        if extracted_knowledge.get("database_models"):
            contracts["models"] = extracted_knowledge["database_models"]

        self.file_store.write_file(
            feature_name,
            FileStore.API_CONTRACTS_FILE,
            yaml.dump(contracts, default_flow_style=False),
        )

    def update_tests_doc(
        self,
        feature_name: str,
        tests_info: dict,
    ) -> None:
        """Update tests.md with test coverage information."""
        existing = self.file_store.read_file(feature_name, FileStore.TESTS_FILE) or ""

        new_content = existing.strip()

        if tests_info.get("test_functions"):
            new_content += "\n\n## Test Functions\n\n"
            for func in tests_info["test_functions"]:
                new_content += f"- {func}\n"

        if tests_info.get("coverage_percentage"):
            new_content += f"\n\n## Coverage\n\n"
            new_content += f"Current coverage: {tests_info['coverage_percentage']}%\n"

        if tests_info.get("test_categories"):
            new_content += f"\n\n## Test Categories\n\n"
            new_content += ", ".join(tests_info["test_categories"]) + "\n"

        self.file_store.write_file(feature_name, FileStore.TESTS_FILE, new_content)

    def extract_and_update(
        self,
        feature_name: str,
        code_content: str,
        file_type: str = "python",
    ) -> dict:
        """Extract knowledge and update documentation files."""
        if not self.file_store.feature_exists(feature_name):
            raise ValueError(f"Feature '{feature_name}' not found")

        if file_type == "python":
            extracted = self.extract_from_python(code_content)
        elif file_type == "yaml":
            extracted = self.extract_from_yaml(code_content)
        else:
            extracted = {}

        # Update relevant documentation
        if file_type == "python":
            self.update_architecture_doc(feature_name, extracted)
            self.update_api_contracts(feature_name, extracted)

        return extracted
