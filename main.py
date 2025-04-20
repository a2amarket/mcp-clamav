from mcp.server.fastmcp import FastMCP
import base64
import tempfile
import os
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
mcp = FastMCP("ClamAV Scanner")

@mcp.tool()
def scan_file(base64_data: str, filename: str) -> dict:
    """
    Scan a base64-encoded file using ClamAV.
    
    Args:
        base64_data (str): Base64 encoded string representing a file
        filename (str): Name of the file to use in the scan
        
    Returns:
        dict: Scan results including the raw clamscan output
    """
    logger.info(f"Received scan request for file: {filename}")
    temp_file_path = None
    try:
        # Decode the base64 string
        file_content = base64.b64decode(base64_data)
        
        # Create a temporary file to store the decoded content
        with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix=f"_{filename}") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
            
        # Set permissions to allow ClamAV to read the file
        os.chmod(temp_file_path, 0o644)
        logger.info(f"Created temporary file: {temp_file_path}")
            
        # Run clamscan command
        result = subprocess.run(['clamscan', temp_file_path], 
                              capture_output=True, 
                              text=True)
        
        logger.info("Scan completed successfully")
        return {
            "success": True,
            "result": result.stdout + result.stderr
        }
        
    except Exception as e:
        logger.error(f"Error during scan: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            logger.info(f"Cleaned up temporary file: {temp_file_path}")