# WELLAIOS Tool Server Demo (Standalone)

This repository offers a standalone server demonstration for developing tools that are compatible with the WELLAIOS engine.
It illustrates how to build and integrate custom functionalities, enabling AI agents within the WELLAIOS ecosystem to leverage these tools in a **multi-user** environment.

## Features

- **Multi-User Support**

  Designed to handle simultaneous requests from multiple distinct users, facilitating personalized interactions with your tools.

- **MCP Compatibility**

  Fully compatible with the Model Context Protocol (MCP), ensuring seamless integration and communication with MCP-enabled platforms.

- **WELLAIOS Engine Integration**

  Enables sophisticated AI agent use cases by providing custom tools that the WELLAIOS engine can discover and utilize.

## Getting Started

Follow these steps to set up and run your WELLAIOS tool server:

1.  Install python

    Ensure you have Python installed on your system. Python 3.12+ is recommended.

2.  Install the required packages

    Navigate to the project directory in your terminal and install the necessary Python packages using pip:

    ```
    pip install -r requirements.txt
    ```

3.  Start the server

    Once the packages are installed, you can launch the tool server:

    ```
    python main.py
    ```

    By default, the server will run on http://localhost:30000.

    **Note**: To register your server with WELLAIOS, it must be accessible from a public IP address.

4.  Authentication (Optional but strongly recommended)

    For enhanced security, it's **strongly recommended** to restrict access to your tool server to known clients.
    Stay safe.

    1. **Register your server on WELLAIOS**

       Follow the instructions provided by the WELLAIOS platform to register your tool server.

    2. **Obtain the bearer token from WELLAIOS**

       After registration, WELLAIOS will provide you with a unique bearer token.

    3. **Add the authentication token to your environment**

       Create a file named `.env` in the root directory of your project (the same directory as `main.py`) and add the following content, replacing `your_wellaios_bearer_token_here` with the token obtained from WELLAIOS:

       ```
       AUTH_TOKEN=your_wellaios_bearer_token_here
       ```

       The `AUTH_TOKEN` environment variable is used by the server's authentication middleware to validate incoming requests.

5.  Test your tool server

    You can test your running tool server

    - **MCP Inspector**:
      For basic testing and inspecting the tool's functionality, you can use the [MCP inspector](https://github.com/modelcontextprotocol/inspector).

      **Note**: The MCP Inspector currently does not support multi-user scenarios. Therefore, you won't be able to test the multi-user specific features using this tool alone.

    - **WELLAIOS Engine**:
      The best way to thoroughly test the multi-user capabilities and the full integration is by connecting your tool server to the WELLAIOS engine itself.
      Refer to the WELLAIOS documentation for instructions on how to connect external tool servers.

## Guide to connect to MCP Inspector

### Transport Type

Select `Streamble HTTP`

### URL

Enter the MCP path under your server's location.
For example, if your server is running locally on port 30000, the URL would be:

`http://localhost:30000/mcp`

### Authentication

Use `Bearer Token` as the authentication method.
Then, use the exact token you've set in your `.env` file.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file.
