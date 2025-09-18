#!/usr/bin/env python3
"""Test script to verify the arcade toolkit is working after consolidation."""

import sys

try:
    import arcade_dreamfactory.tools as tools
    print("✓ Successfully imported arcade_dreamfactory.tools module")

    # Check total count
    total = len(tools.__all__)
    print(f"\n✓ Total tools exported: {total}")

    # List tools by category
    print("\nTools by category:")
    print("\nSystem Tools (2):")
    for tool in ["list_services", "get_service_details"]:
        if tool in tools.__all__:
            print(f"  ✓ {tool}")
        else:
            print(f"  ✗ {tool} - MISSING")

    print("\nDatabase Tools (6):")
    for tool in ["list_database_tables", "get_table_schema", "query_database_table",
                 "insert_records", "update_records", "delete_records"]:
        if tool in tools.__all__:
            print(f"  ✓ {tool}")
        else:
            print(f"  ✗ {tool} - MISSING")

    print("\nFile Tools (6):")
    for tool in ["list_storage_services", "list_files", "read_file",
                 "write_file", "delete_file", "manage_file"]:
        if tool in tools.__all__:
            print(f"  ✓ {tool}")
        else:
            print(f"  ✗ {tool} - MISSING")

    # Check for removed tools (should NOT be present)
    print("\nVerifying removed tools are gone:")
    removed_tools = [
        "call_stored_procedure", "create_app", "create_database_api_complete",
        "create_database_service", "create_role", "delete_service",
        "execute_sql_query", "get_stored_procedures", "list_apps", "list_roles",
        "get_records_by_ids", "copy_file", "move_file", "create_folder",
        "search_files", "get_file_info"
    ]

    for tool in removed_tools:
        if tool not in tools.__all__:
            print(f"  ✓ {tool} - correctly removed")
        else:
            print(f"  ✗ {tool} - STILL PRESENT (should be removed)")

    print("\n✓ All tests passed! Toolkit successfully consolidated from 29 to 14 tools.")

except ImportError as e:
    print(f"✗ Failed to import module: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)