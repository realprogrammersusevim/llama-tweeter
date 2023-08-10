import os
import sys

from llama_cpp import Llama


def summarize_text(text, model_path):
    # Save a copy of the current file descriptors for stdout and stderr
    stdout_fd = os.dup(1)
    stderr_fd = os.dup(2)

    # Open up /dev/null to redirect
    devnull_fd = os.open(os.devnull, os.O_WRONLY)

    # Replace stdout and stderr with /dev/null
    os.dup2(devnull_fd, 1)
    os.dup2(devnull_fd, 2)

    # Only writing to sys.stdout and sys.stderr should still work
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = os.fdopen(stdout_fd, "w")
    sys.stderr = os.fdopen(stderr_fd, "w")

    try:
        # Load the LLM once and then reuse it for multiple queries instead of reloading
        llm = Llama(
            model_path=model_path,
            verbose=False,
            use_mlock=True,
            n_ctx=1000,
        )
    finally:
        # Restore stdout and stderr to their original state
        os.dup2(stdout_fd, 1)
        os.dup2(stderr_fd, 2)

        # Close those saved file descriptors
        os.close(stdout_fd)
        os.close(stderr_fd)

        # Close the /dev/null file descriptors
        os.close(devnull_fd)

        # Restore the sys.stdout and sys.stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr

    # TODO: Check character limit and do some error correction
    return llm(
        text
        + "\n[INST]Respond with only the text of a tweet summarizing the the most interesting news story above in 280 characters.[/INST]\n",
        max_tokens=280,
    )
