from langchain_experimental.tools.python.tool import PythonREPLTool
import matplotlib
matplotlib.use('Agg')

class ExtendedPythonTool(PythonREPLTool):
    """
    A Python REPL tool extended to generate plots and return as base64 data URI when plt is used.
    """
    def _run(self, command: str) -> str:
        import matplotlib.pyplot as plt
        import io, base64, textwrap

        # Remove backticks, language tags, and leading/trailing whitespace
        command = command.strip().strip("`")
        if command.startswith("python"):
            command = command[len("python"):].lstrip()

        # Always dedent and execute as a block to support multi-line and control structures
        command = textwrap.dedent(command)

        # If plotting, handle as base64
        if "plt" in command or "matplotlib" in command:
            buf = io.BytesIO()
            try:
                exec(command, globals())
                plt.savefig(buf, format="png", bbox_inches="tight")
                plt.close()
                buf.seek(0)
                img_bytes = buf.read()
                data_uri = "data:image/png;base64," + base64.b64encode(img_bytes).decode()
                if len(data_uri.encode()) > 100000:
                    return "Image is too large. Please simplify or resize."
                return data_uri
            finally:
                buf.close()
        # Otherwise run normally
        return super()._run(command)