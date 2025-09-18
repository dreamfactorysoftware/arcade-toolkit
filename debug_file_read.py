#!/usr/bin/env python3
"""Debug script to help diagnose file reading issues."""

def debug_file_read_url(service_name, file_path, base_url="/api/v2"):
    """Show what URL the tool would construct."""

    # Clean up path (same as tool does)
    if file_path.startswith("/"):
        file_path = file_path[1:]

    # Construct URL
    url = f"{base_url}/{service_name}/{file_path}"

    print("File Read Debugging:")
    print("-" * 50)
    print(f"Service Name: {service_name}")
    print(f"File Path: {file_path}")
    print(f"Constructed URL: {url}")
    print(f"Query Params: ?include_content=true")
    print()
    print("Common issues to check:")
    print("1. File exists? Try listing files first:")
    print(f"   list_files('{service_name}', '/')")
    print()
    print("2. Correct service name? List all storage services:")
    print("   list_storage_services()")
    print()
    print("3. File might be in a subfolder? Try:")
    print(f"   list_files('{service_name}', '/', recursive=True, search_term='{file_path.split('/')[-1]}')")
    print()
    print("4. Try with metadata only first:")
    print(f"   read_file('{service_name}', '{file_path}', metadata_only=True)")

# Your case
debug_file_read_url("blob", "composercopy.json")
print()
print("Possible corrections:")
debug_file_read_url("blob", "/composercopy.json")  # With leading slash
debug_file_read_url("files", "composercopy.json")  # Different service name
debug_file_read_url("blob", "blob/composercopy.json")  # Nested path