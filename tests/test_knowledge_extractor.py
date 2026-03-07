"""Tests for knowledge extraction."""

import pytest

from core.knowledge_extractor import KnowledgeExtractor


class TestKnowledgeExtractor:
    """Tests for KnowledgeExtractor."""

    def test_extract_python_imports(self):
        """Test extracting imports from Python code."""
        code = """
import os
import sys
from typing import List, Dict
from pathlib import Path
"""
        extractor = KnowledgeExtractor()
        result = extractor.extract_from_python(code)

        assert len(result["imports"]) >= 4
        import_modules = [imp["module"] for imp in result["imports"]]
        assert "os" in import_modules
        assert "sys" in import_modules
        assert "typing" in import_modules

    def test_extract_from_import(self):
        """Test extracting from...import statements."""
        code = "from fastapi import FastAPI, APIRouter"
        extractor = KnowledgeExtractor()
        result = extractor.extract_from_python(code)

        assert len(result["imports"]) >= 1
        assert result["imports"][0]["module"] == "fastapi"
        assert "FastAPI" in result["imports"][0]["items"]
        assert "APIRouter" in result["imports"][0]["items"]

    def test_extract_api_routes(self):
        """Test extracting API routes."""
        code = """
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
def get_users():
    pass

@router.post("/users")
def create_user():
    pass
"""
        extractor = KnowledgeExtractor()
        result = extractor.extract_from_python(code)

        assert len(result["api_routes"]) >= 2
        routes = [(r["method"], r["path"]) for r in result["api_routes"]]
        assert ("GET", "/users") in routes
        assert ("POST", "/users") in routes

    def test_extract_function_definitions(self):
        """Test extracting function definitions."""
        code = """
def hello():
    pass

async def async_function(param1: str, param2: int):
    pass
"""
        extractor = KnowledgeExtractor()
        result = extractor.extract_from_python(code)

        assert len(result["function_definitions"]) >= 2
        func_names = [f["name"] for f in result["function_definitions"]]
        assert "hello" in func_names
        assert "async_function" in func_names

    def test_extract_class_definitions(self):
        """Test extracting class definitions."""
        code = """
class User:
    pass

class Admin(User):
    pass
"""
        extractor = KnowledgeExtractor()
        result = extractor.extract_from_python(code)

        assert len(result["class_definitions"]) >= 2
        class_names = [c["name"] for c in result["class_definitions"]]
        assert "User" in class_names
        assert "Admin" in class_names

    def test_extract_database_models(self):
        """Test extracting database models."""
        code = """
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
"""
        extractor = KnowledgeExtractor()
        result = extractor.extract_from_python(code)

        assert "User" in result["database_models"]

    def test_extract_from_yaml(self):
        """Test extracting from YAML."""
        yaml_content = """
routes:
  - path: /users
    method: GET
"""
        extractor = KnowledgeExtractor()
        result = extractor.extract_from_yaml(yaml_content)

        assert result["parsed"] is True
        assert result["data"]["routes"][0]["path"] == "/users"

    def test_invalid_yaml(self):
        """Test handling invalid YAML."""
        yaml_content = "invalid: yaml: content:"
        extractor = KnowledgeExtractor()
        result = extractor.extract_from_yaml(yaml_content)

        assert result["parsed"] is False

    def test_extract_tests_info(self):
        """Test extracting test info."""
        tests_content = """
# Tests

## Test Functions

- test_login_success
- test_login_failure
- test_logout

## Coverage

Current coverage: 85%

## Test Categories

unit, integration
"""
        extractor = KnowledgeExtractor()
        result = extractor.extract_tests_info(tests_content)

        assert "test_login_success" in result["test_functions"]
        assert "test_login_failure" in result["test_functions"]
        assert result["coverage_percentage"] == 85
        assert "unit" in result["test_categories"]
        assert "integration" in result["test_categories"]

    def test_extract_test_files(self):
        """Test extracting test file references."""
        tests_content = """
Tests are in:
- tests/test_auth.py
- tests/test_users.py
"""
        extractor = KnowledgeExtractor()
        result = extractor.extract_tests_info(tests_content)

        assert "tests/test_auth.py" in result["test_files"]
        assert "tests/test_users.py" in result["test_files"]
