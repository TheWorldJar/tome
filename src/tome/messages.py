GITHUB_ISSUES_URL = "https://github.com/TheWorldJar/tome/issues"

USAGE_ERROR = "Usage: tome {audio_file} {prompt_file}"

INVALID_AUDIO_FILE_PATH = "Make sure to provide a valid audio file path in between quotes!"

INVALID_PROMPT_FILE_PATH = "Make sure to provide a valid prompt file path in between quotes!"

INVALID_PROMPT_EXTENSION_TEMPLATE = (
    "Invalid prompt file extension! Got {prompt_extension}. Valid extensions are: {valid_extensions}"
)

CUDA_OOM_TRANSCRIPTION_TEMPLATE = (
    "\n\nCUDA out of memory! Please change the transcription_model in config.yaml to a smaller model"
    + "\nCurrent transcription_model: {current_model}"
    + "\nDefault transcription_model: {default_model}"
    + f"\nIf that did not help, please report it at {GITHUB_ISSUES_URL}"
)

CUDA_OOM_EXECUTION_TEMPLATE = (
    "\n\nCUDA out of memory! Please change the output_model and/or context_size in config.yaml to a smaller model."
    + "\nCurrent output_model: {current_output_model}"
    + "\nCurrent context_size: {current_context_size}"
    + "\nDefault output_model: {default_output_model}"
    + "\nDefault context_size: {default_context_size}"
    + f"\nIf that did not help, please report it at {GITHUB_ISSUES_URL}"
)

UNHANDLED_CUDA_OOM_ERROR = f"\n\nUnhandled CUDA out of memory error! Please report it at {GITHUB_ISSUES_URL}\n\n"

UNHANDLED_EXCEPTION_ERROR = f"\n\nUnhandled exception! Please report it at {GITHUB_ISSUES_URL}\n\n"

EXCEPTION_TYPE_PREFIX = "\n\nType: "
