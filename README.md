# Tome

Tome is a python script that takes in a video or audio file as input, transcribes it using [Whisper](https://github.com/openai/whisper) and then feeds the transcript and a prompt to an LLM using [Ollama](https://github.com/ollama/ollama-python) to obtain notes, highlights, and other outputs as specified by the prompt.

## Motivation

As a forever GM, I have very little opportunity to take notes on what happened in a Pathfinder session while I'm actively running it. Taking notes after the fact quickly becomes unreliable if the session was front-loaded, became somewhat of a strain on my schedule for a late Sunday night, and was boring after the fun of the session itself. One solution was this: use AI to create transcripts of a session and then make notes from that transcript. Two problem: a 4-hour session produces a lot of text and I don't want to pay 20$ a month *just* for that.

So I made **Tome** to run the AI process I wanted entirely on my machine. From there, I added a SQLite database, a configuration file, and changed the functionality to use prompt files to exetend this script into use cases beyond mine!

## Requirements

- Python 3.9+
- [Ollama Desktop](https://ollama.com/download). The app needs to be installed and running. The selected model needs to have been pulled within your virtual environment. Cloud models are not supported.
- A decent CPU/GPU combo. The actions this script performs can be very intensive on your system, which can result in multi-hours long execution depending on your hardware.

## Installation

It is recommended to install this application in a virtual environment. In the root of this script, execute:

`python -m venv .venv`

Then, activate the environment:

### Linux/Macos

`source .venv/bin/activate`

### Windows

`.venv\Scripts\activate.bat`

Once the environment is active, simply install the package through pip:

`pip install -e .`

Then, you can pull your desired Ollama model inside your environment after [manually installing](https://ollama.com/download) Ollama:

`ollama pull {model}`

## Quick Start

Once installed, the script can be used with the following command:

`tome {path_to_audio_file} {path_to_prompt}`

Like this:

`tome ./my_audio.mp3 ./my_prompt.txt`

The script will create a local SQLite database to store some of its actions, as well as a transcript and output folder, as specified in `config.yaml`.

## Usage

The script has the following behaviour:

- When processing an audio file for the first time, its signature is stored in the local database and a transcript is produced.
- When processing an audio file for the second time with the same model, the script attempts to retrieve the transcript that was previously generated instead. A new transcript will be generated if it cannot find the original.
- When processing a transcript for the first time, its signature is stored in the local database and an output is produced.
- When processing a transcript for the second time, the script will modify the existing output on disk. A new output will be produced if it cannot find the original.
- Although Whisper allows video files, the video contents are not used in the creation of a transcript.

## Configuration

`config.yaml` uses the following keys:

- `transcripts_folder`: The location you want transcripts to be output to. Default: `'./transcripts'`
- `output_folder`: The location you want final outputs to be output to. Default: `'./output'`
- `transcription_model`: The Whisper model that will be used for the transcription task. Default: `'turbo'`
- `output_model`: The Ollama model that will be used for the output task. Cloud models not supported. Default: `'gemma3:4b'`

Invalid configs will be replaced by a default config during runtime!

## Troubleshooting

### Whisper Models

See the list of valid [Whisper models](https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages). Expected VRAM usages are listed.

### Ollama Models

Only local models are supported. See the [list of models](https://ollama.com/library). Not all models are available locally.

### Any Other Problem

Please report any other problem in the [issues](https://github.com/TheWorldJar/tome/issues) section of this repo. Unhandled exceptions will prompt you to do so!

### Performance Tips

Systems with only 8GB of VRAM should stick to Ollama models around 8b and under.

The longer the input file, the longer the transcription time. When using Whisper's Large model, prepare for a transcription time at least as long as the input file itself.

Attempting to load a model too large for your VRAM will result in an offload to system RAM and a dramatic slowdown in performance.

LLMs are never guaranteed to produce the same output twice.

## Contributing

If you'd like to contribute, please fork the repository and install the package with its dev dependencies:

```bash
pip install -e .[dev]
```

Once done, please submit a pull request to a new branch!

## License

See our [license](https://github.com/TheWorldJar/tome/blob/main/LICENSE)
