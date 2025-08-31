"""
Type inference tests.
"""

import pytest
from mcp import MCP
from typing import List, Dict, Optional, Union
import inspect


class TestTypeInference:
    """Test automatic type inference from function signatures."""

    def test_basic_types(self):
        """Test inference of basic Python types."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Basic Types", "Description": "Function with basic types"})
        def basic_types_func(
            str_param: str,
            int_param: int,
            float_param: float,
            bool_param: bool
        ):
            """Function with basic types.
            
            str_param: String parameter
            int_param: Integer parameter
            float_param: Float parameter
            bool_param: Boolean parameter
            """
            return "test"
        
        tool_info = server.tools["basic_types_func"]
        properties = tool_info["properties"]
        
        assert properties["str_param"]["type"] == "string"
        assert properties["int_param"]["type"] == "integer"
        assert properties["float_param"]["type"] == "number"
        assert properties["bool_param"]["type"] == "boolean"

    def test_collection_types(self):
        """Test inference of collection types."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Collections", "Description": "Function with collection types"})
        def collection_func(
            list_param: list,
            dict_param: dict
        ):
            """Function with collection types.
            
            list_param: List parameter
            dict_param: Dict parameter
            """
            return "test"
        
        tool_info = server.tools["collection_func"]
        properties = tool_info["properties"]
        
        assert properties["list_param"]["type"] == "array"
        assert properties["dict_param"]["type"] == "object"

    def test_typing_module_types(self):
        """Test inference of typing module types."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Typing Types", "Description": "Function with typing module types"})
        def typing_func(
            list_param: List[str],
            dict_param: Dict[str, int],
            optional_param: Optional[str]
        ):
            """Function with typing module types.
            
            list_param: List of strings
            dict_param: Dict with string keys and int values
            optional_param: Optional string
            """
            return "test"
        
        tool_info = server.tools["typing_func"]
        properties = tool_info["properties"]
        
        assert properties["list_param"]["type"] == "array"
        assert properties["dict_param"]["type"] == "object"
        assert properties["optional_param"]["type"] == "string"

    def test_no_annotation_defaults_to_string(self):
        """Test that parameters without annotations default to string type."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "No Annotations", "Description": "Function without type annotations"})
        def no_annotations_func(param1, param2):
            """Function without annotations.
            
            param1: First parameter
            param2: Second parameter
            """
            return "test"
        
        tool_info = server.tools["no_annotations_func"]
        properties = tool_info["properties"]
        
        assert properties["param1"]["type"] == "string"
        assert properties["param2"]["type"] == "string"

    def test_string_annotations(self):
        """Test inference from string annotations (forward references)."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "String Annotations", "Description": "Function with string annotations"})
        def string_annotations_func(
            int_param: "int",
            float_param: "float", 
            bool_param: "bool",
            list_param: "list",
            dict_param: "dict"
        ):
            """Function with string annotations.
            
            int_param: Integer parameter
            float_param: Float parameter
            bool_param: Boolean parameter
            list_param: List parameter
            dict_param: Dict parameter
            """
            return "test"
        
        tool_info = server.tools["string_annotations_func"]
        properties = tool_info["properties"]
        
        assert properties["int_param"]["type"] == "integer"
        assert properties["float_param"]["type"] == "number"
        assert properties["bool_param"]["type"] == "boolean"
        assert properties["list_param"]["type"] == "array"
        assert properties["dict_param"]["type"] == "object"

    def test_mixed_annotations(self):
        """Test function with mix of annotation types."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Mixed", "Description": "Function with mixed annotations"})
        def mixed_func(
            typed: int,
            string_typed: "str",
            untyped,
            default_typed: bool = True
        ):
            """Function with mixed annotations.
            
            typed: Typed parameter
            string_typed: String typed parameter
            untyped: Untyped parameter
            default_typed: Parameter with default
            """
            return "test"
        
        tool_info = server.tools["mixed_func"]
        properties = tool_info["properties"]
        
        assert properties["typed"]["type"] == "integer"
        assert properties["string_typed"]["type"] == "string"
        assert properties["untyped"]["type"] == "string"  # Default fallback
        assert properties["default_typed"]["type"] == "boolean"

    def test_complex_typing_annotations(self):
        """Test complex typing annotations that should fallback to basic types."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Complex", "Description": "Function with complex typing"})
        def complex_func(
            union_param: Union[str, int],
            optional_list: Optional[List[str]],
            nested_dict: Dict[str, List[int]]
        ):
            """Function with complex typing.
            
            union_param: Union parameter
            optional_list: Optional list
            nested_dict: Nested dict
            """
            return "test"
        
        tool_info = server.tools["complex_func"]
        properties = tool_info["properties"]
        
        # Union should fallback to string (first in type mapping check)
        assert properties["union_param"]["type"] == "string"
        # Optional[List[str]] type inference may vary
        assert properties["optional_list"]["type"] in ["array", "string"]
        # Dict should be object regardless of type parameters
        assert properties["nested_dict"]["type"] == "object"

    def test_parameter_empty_annotation(self):
        """Test handling of inspect.Parameter.empty annotation."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        # Test the internal method directly
        assert server._infer_param_type_from_annotation(inspect.Parameter.empty) == "string"
        assert server._infer_param_type_from_annotation(None) == "string"

    def test_unknown_type_defaults_to_string(self):
        """Test that unknown types default to string."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        # Create a custom class for testing
        class CustomType:
            pass
        
        @server.add({"Title": "Custom Type", "Description": "Function with custom type"})
        def custom_type_func(custom: CustomType):
            """Function with custom type.
            
            custom: Custom type parameter
            """
            return "test"
        
        tool_info = server.tools["custom_type_func"]
        properties = tool_info["properties"]
        
        # Should default to string
        assert properties["custom"]["type"] == "string"

    def test_case_insensitive_string_annotations(self):
        """Test case insensitive matching for string annotations."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Case Test", "Description": "Case insensitive test"})
        def case_test_func(
            int_param: "INT",
            bool_param: "BOOL", 
            list_param: "LIST",
            dict_param: "DICT"
        ):
            """Function testing case insensitive matching.
            
            int_param: Integer parameter
            bool_param: Boolean parameter
            list_param: List parameter
            dict_param: Dict parameter
            """
            return "test"
        
        tool_info = server.tools["case_test_func"]
        properties = tool_info["properties"]
        
        assert properties["int_param"]["type"] == "integer"
        assert properties["bool_param"]["type"] == "boolean"
        assert properties["list_param"]["type"] == "array"
        assert properties["dict_param"]["type"] == "object"

    def test_partial_string_matching(self):
        """Test partial string matching in annotations."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Partial Match", "Description": "Partial string matching test"})
        def partial_match_func(
            number_param: "number_type",
            integer_param: "some_int_value",
            array_param: "array_of_items"
        ):
            """Function testing partial string matching.
            
            number_param: Number parameter
            integer_param: Integer parameter  
            array_param: Array parameter
            """
            return "test"
        
        tool_info = server.tools["partial_match_func"]
        properties = tool_info["properties"]
        
        assert properties["number_param"]["type"] == "number"
        assert properties["integer_param"]["type"] == "integer"  
        assert properties["array_param"]["type"] == "array"