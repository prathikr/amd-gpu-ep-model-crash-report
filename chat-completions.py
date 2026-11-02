"""Register local Gemma 3 assets and run a text prompt with Foundry Local SDK v2.

Usage:
    python chat-completion.py
    python chat-completion.py --prompt "Explain ONNX briefly." --max-tokens 256
"""

from __future__ import annotations

import argparse
from pathlib import Path

from foundry_local_sdk import (
    CatalogType,
    ChatSession,
    Configuration,
    FoundryLocalManager,
    MessageItem,
    ModelInfoBuilder,
    Request,
    RequestOptions,
    SearchOptions,
    TextItem,
    TextItemType,
)

### WORKING
# MODEL_PATH = Path("C:\\Users\\prathikrao\\OneDrive - Microsoft\\Desktop\\foundry-local\\models\\DeepSeek-R1-Distill-Llama-8B-dml-int4-awq-block-128")
# MODEL_ID = "deepseek-r1-distill-llama-8b-dml-int4-awq-block:1"
# MODEL_PATH = Path("C:\\Users\\prathikrao\\OneDrive - Microsoft\\Desktop\\foundry-local\\models\\DeepSeek-R1-Distill-Qwen-7B-awq-asym-uint4-g128-lmhead-onnx-dml")
# MODEL_ID = "deepseek-r1-distill-qwen-7b-awq-asym-uint4-g128-lmhead-onnx-dml:1"
# MODEL_PATH = Path("C:\\Users\\prathikrao\\OneDrive - Microsoft\\Desktop\\foundry-local\\models\\Llama-3.2-1B-Instruct-awq-g128-int4-onnx-directml")
# MODEL_ID = "llama-3.2-1b-instruct-awq-g128-int4-onnx-directml:1"
# MODEL_PATH = Path("C:\\Users\\prathikrao\\OneDrive - Microsoft\\Desktop\\foundry-local\\models\\Qwen2.5-Coder-14B-Instruct_gpuep_1.0_gpu_128")
# MODEL_ID = "qwen2.5-coder-14b-instruct_gpuep_1.0_gpu_128:1"

### FAILING
# MODEL_PATH = Path("C:\\Users\\prathikrao\\OneDrive - Microsoft\\Desktop\\foundry-local\\models\\Gemma3-4B-it_gpuep_1.0_gpu_128")
# MODEL_ID = "gemma3-4b-it-amdgpu:1"
# MODEL_PATH = Path("C:\\Users\\prathikrao\\OneDrive - Microsoft\\Desktop\\foundry-local\\models\\Gemma-4-26B-A4B-it_gpuep_1.0_gpu_128")
# MODEL_ID = "gemma-4-26b-a4b-it-amdgpu:1"
# MODEL_PATH = Path("C:\\Users\\prathikrao\\OneDrive - Microsoft\\Desktop\\foundry-local\\models\\Qwen3.5-9B_gpuep_1.0_gpu_128")
# MODEL_ID = "qwen3.5-9b:1"

MODEL_PATH = Path("C:\\Users\\prathikrao\\OneDrive - Microsoft\\Desktop\\foundry-local\\models\\DeepSeek-R1-Distill-Llama-70B-dml-int4-awq-block-128")
MODEL_ID = "deepseek-r1-distill-llama-70b-dml-int4-awq-block:1"

EXECUTION_PROVIDER = "AMDGPUExecutionProvider"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prompt",
        default="Explain what an ONNX execution provider does in two sentences.",
    )
    parser.add_argument("--max-tokens", type=int, default=256)
    args = parser.parse_args()
    if not args.prompt.strip():
        parser.error("--prompt must not be empty")
    if args.max_tokens <= 0:
        parser.error("--max-tokens must be positive")

    with FoundryLocalManager(
        Configuration(app_name="Gemma3AMDGPU")
    ) as manager:
        print("Available execution providers:")
        for ep in manager.discover_eps():
            print(f"  - {ep.name} (registered: {ep.is_registered})")

        result = manager.download_and_register_eps(names=[EXECUTION_PROVIDER])
        if not result.success:
            raise RuntimeError(
                f"Could not register {EXECUTION_PROVIDER}: {result.status}; "
                f"failed providers: {result.failed_eps}"
            )
        else:
            print(f"Successfully registered {EXECUTION_PROVIDER}")

        catalog = manager.get_catalog(CatalogType.LOCAL)
        model = catalog.get_model_variant(MODEL_ID)
        if model:
            catalog.unregister_model(MODEL_ID)
        with ModelInfoBuilder() as metadata:
            metadata.set_string_property("task", "chat-completion")
            metadata.set_string_property("display_name", MODEL_ID[:-2])
            model = catalog.register_model(MODEL_PATH, MODEL_ID, metadata)


        print(f"Using {model.id} at {model.get_path()}")
        print(f"Loading with {EXECUTION_PROVIDER} (HIP; CPU fallback disabled)...")
        try:
            model.load()
            with ChatSession(model) as session:
                session.set_options(
                    RequestOptions(
                        search=SearchOptions(
                            max_output_tokens=args.max_tokens,
                            temperature=0.7,
                        )
                    )
                )
                with Request() as request:
                    request.add_item(MessageItem.user(args.prompt))
                    with session.process_request(request) as response:
                        parts: list[str] = []
                        for item in response:
                            if isinstance(item, MessageItem):
                                parts.extend(
                                    part.text
                                    for part in item.parts
                                    if isinstance(part, TextItem)
                                    and part.type == TextItemType.DEFAULT
                                )
                            elif (
                                isinstance(item, TextItem)
                                and item.type == TextItemType.DEFAULT
                            ):
                                parts.append(item.text)
                        if not parts:
                            raise RuntimeError("The model returned no response text.")
                        print("\nAssistant:", "".join(parts))
        finally:
            if model.is_loaded:
                model.unload()


if __name__ == "__main__":
    main()