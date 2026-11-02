# AMDGPU EP: model crash report

Report date: 2026-11-02

## Summary

All three models listed below exhibit the same crash signature with AMDGPUExecutionProvider on Windows x64: access violation `0xC0000005` at `onnxruntime.dll + 0x6C5905` during `OgaCreateGenerator`. One representative crash log (Gemma 4) is included verbatim below for AMD investigation.

## Affected models

| Model | Local registration ID | HF Url |
|---|---|---|
| Gemma 4 26B A4B IT | `gemma-4-26b-a4b-it-amdgpu:1` | https://huggingface.co/amd/Gemma-4-26B-A4B-it_gpuep_1.0_gpu_128 |
| Gemma 3 4B IT | `gemma3-4b-it-amdgpu:1` | https://huggingface.co/amd/Gemma3-4B-it_gpuep_1.0_gpu_128 |
| Qwen 3.5 9B | `qwen3.5-9b:1` | https://huggingface.co/amd/Qwen3.5-9B_gpuep_1.0_gpu_128 |

## Working comparison models

The following models ran successfully with AMDGPUExecutionProvider in the same environment:

- DeepSeek-R1-Distill-Llama-8B-dml-int4-awq-block-128
- DeepSeek-R1-Distill-Qwen-7B-awq-asym-uint4-g128-lmhead-onnx-dml
- Llama-3.2-1B-Instruct-awq-g128-int4-onnx-directml
- Qwen2.5-Coder-14B-Instruct_gpuep_1.0_gpu_128

This suggests a model-specific EP or EP/ORT integration issue rather than a general ORT failure, but does not rule out an ORT or GenAI bug on the failing models' execution paths.

### Current model configuration

All three decoder configurations specify:

```json
{
  "session.disable_cpu_ep_fallback": "1",
  "provider_options": [
    {
      "AMDGPU": {
        "profile": "hip"
      }
    }
  ]
}
```

## Machine details

| Component | Details |
|---|---|
| System | GMKtec EVO-X2 |
| CPU | AMD RYZEN AI MAX+ 395 w/ Radeon 8060S |
| Physical memory reported by Windows | 63.65 GiB |
| GPU | AMD Radeon(TM) 8060S Graphics |
| GPU PCI vendor / device | `1002` / `1586` |
| AMD graphics driver version | `32.0.31007.1017` |
| OS | Microsoft Windows 11 Enterprise, 64-bit |
| OS version / build | `10.0.26300` / `26300` |

## Software and runtime

| Component | Version / details |
|---|---|
| Python | 3.12.10, virtual environment |
| Foundry Local Python SDK | build from source after this PR merged: https://github.com/microsoft/foundry-local/pull/1259 |
| ONNX Runtime Python package | `onnxruntime==1.31.0` |
| ONNX Runtime GenAI Python package | `onnxruntime-genai-core==0.18.0` |
| WinML DLL in native build output | `2.5.96.5615` (product `2.5.96+15ef6e1278`) |
| Execution provider | `AMDGPUExecutionProvider` |
| Decoder profile | `hip` |
| Native Foundry configuration | Windows x64, RelWithDebInfo |

## Original crash log

```text
=== hip-compiler: exception 0xc0000005 at 00007FFE1DF75905 ===
Stack trace (most recent call first):
#0  0x00007ffdd19feca7 in hip_get_version
#1  0x00007fff050c44d5 in RtlWow64GetCurrentMachine
#2  0x00007fff050c3c74 in RtlWow64GetCurrentMachine
#3  0x00007fff05165ded in KiUserExceptionDispatcher
#4  0x00007ffe1df75904 in OrtGetApiBase
#5  0x00007ffe1df78ffd in OrtGetApiBase
#6  0x00007ffe1df7aa7c in OrtGetApiBase
#7  0x00007ffe355901cf in OgaUpdateTokenizerOptions
#8  0x00007ffe354e0cab in  ?? 
#9  0x00007ffe3551a8a5 in  ?? 
#10 0x00007ffe3551ba58 in  ?? 
#11 0x00007ffe3551cc6c in  ?? 
#12 0x00007ffe354ac0ea in  ?? 
#13 0x00007ffe354ae9d5 in  ?? 
#14 0x00007ffe35575858 in OgaCreateGenerator
#15 0x00007ffe1cb7c1a6 in fl::OnnxChatGenerator::CreatePrepared(fl::PreparedChatPrompt*, fl::PreparedChatPrompt*, fl::SearchOptions&, fl::SearchOptions&) at C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\src\inferencing\generative\chat\onnx_chat_generator.cc:422
#16 0x00007ffe1cabc2c4 in fl::`anonymous namespace'::CreatePreparedTextChatGenerator(fl::chat_internal::PreparedChatMessages&, fl::PreparedChatPrompt*, fl::PreparedChatPrompt*, fl::PreparedChatPrompt*, fl::SearchOptions&, fl::GenAIModelInstance&, fl::GenAIModelInstance&) at C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\src\inferencing\generative\chat\chat_session.cc:92
#17 0x00007ffe1cacb754 in fl::ChatSession::ProcessRequestImpl(fl::ChatSession*, fl::Request&) at C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\src\inferencing\generative\chat\chat_session.cc:1666
#18 0x00007ffe1ca63da7 in fl::Session::ProcessRequest(fl::Session*, fl::Request&, fl::Request&) at C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\src\inferencing\session\session.cc:288
#19 0x00007ffe1c90d790 in fl::api::`anonymous namespace'::EmbeddedSession::ProcessRequest(fl::Request&, fl::Response&, std::optional<fl::StreamingCallback>*) at C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\src\api\embedded_backend.cc:47
#20 0x00007ffe1c8ee710 in Session_ProcessRequestImpl(flSession*, flRequest*, flRequest*) at C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\src\c_api.cc:1902
#21 0x00007ffee64010f2 in  ?? 
#22 0x00007ffee641a64b in PyInit__cffi_backend
#23 0x00007ffee640771e in  ?? 
#24 0x00007ffe35af2017 in PyObject_Vectorcall
#25 0x00007ffe35af19c4 in PyObject_Vectorcall
#26 0x00007ffe35af2ea4 in _PyEval_EvalFrameDefault
#27 0x00007ffe35aa81e3 in _PyObject_ClearManagedDict
#28 0x00007ffe35aa6b65 in PyEval_EvalCode
#29 0x00007ffe35b5e837 in _Py_SourceAsString
#30 0x00007ffe35b5ea6f in _PyModule_ClearDict
#31 0x00007ffe35b3a5d3 in PyDict_DelItemString
#32 0x00007ffe35b3a431 in _PyRun_SimpleFileObject
#33 0x00007ffe35b3cd18 in _PyRun_AnyFileObject
#34 0x00007ffe35b3cee9 in _PyEval_MakePendingCalls
#35 0x00007ffe35b3cbea in PyErr_SetExcFromWindowsErrWithFilenameObjects
#36 0x00007ffe35a98f1a in PyMem_GetAllocator
#37 0x00007ffe35a986ff in Py_RunMain
#38 0x00007ffe35a986e2 in Py_Main
#39 0x00007ff6f299122f in  ?? 
#40 0x00007fff03fedda6 in BaseThreadInitThunk
#41 0x00007fff0507ee4b in RtlUserThreadStart
Exception Code: 0xC0000005
0x00007FFE1DF75905, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\onnxruntime\capi\onnxruntime.dll(0x00007FFE1D8B0000) + 0x6C5905 byte(s), OrtGetApiBase() + 0x1F315 byte(s)
0x00007FFE1DF78FFE, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\onnxruntime\capi\onnxruntime.dll(0x00007FFE1D8B0000) + 0x6C8FFE byte(s), OrtGetApiBase() + 0x22A0E byte(s)
0x00007FFE1DF7AA7D, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\onnxruntime\capi\onnxruntime.dll(0x00007FFE1D8B0000) + 0x6CAA7D byte(s), OrtGetApiBase() + 0x2448D byte(s)
0x00007FFE355901D0, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\onnxruntime_genai_core\bin\onnxruntime-genai.dll(0x00007FFE35200000) + 0x3901D0 byte(s), OgaUpdateTokenizerOptions() + 0x11E80 byte(s)
0x00007FFE354E0CAC, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\onnxruntime_genai_core\bin\onnxruntime-genai.dll(0x00007FFE35200000) + 0x2E0CAC byte(s)
0x00007FFE3551A8A6, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\onnxruntime_genai_core\bin\onnxruntime-genai.dll(0x00007FFE35200000) + 0x31A8A6 byte(s)
0x00007FFE3551BA59, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\onnxruntime_genai_core\bin\onnxruntime-genai.dll(0x00007FFE35200000) + 0x31BA59 byte(s)
0x00007FFE3551CC6D, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\onnxruntime_genai_core\bin\onnxruntime-genai.dll(0x00007FFE35200000) + 0x31CC6D byte(s)
0x00007FFE354AC0EB, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\onnxruntime_genai_core\bin\onnxruntime-genai.dll(0x00007FFE35200000) + 0x2AC0EB byte(s)
0x00007FFE354AE9D6, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\onnxruntime_genai_core\bin\onnxruntime-genai.dll(0x00007FFE35200000) + 0x2AE9D6 byte(s)
0x00007FFE35575859, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\onnxruntime_genai_core\bin\onnxruntime-genai.dll(0x00007FFE35200000) + 0x375859 byte(s), OgaCreateGenerator() + 0x19 byte(s)
0x00007FFE1CB7C1A7, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\build\Windows\RelWithDebInfo\bin\RelWithDebInfo\foundry_local.dll(0x00007FFE1C770000) + 0x40C1A7 byte(s), fl::OnnxChatGenerator::CreatePrepared() + 0x197 byte(s), C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\src\inferencing\generative\chat\onnx_chat_generator.cc, line 422 + 0x1C byte(s)
0x00007FFE1CABC2C5, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\build\Windows\RelWithDebInfo\bin\RelWithDebInfo\foundry_local.dll(0x00007FFE1C770000) + 0x34C2C5 byte(s), fl::`anonymous namespace'::CreatePreparedTextChatGenerator() + 0x115 byte(s), C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\src\inferencing\generative\chat\chat_session.cc, line 92 + 0x22 byte(s)
0x00007FFE1CACB755, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\build\Windows\RelWithDebInfo\bin\RelWithDebInfo\foundry_local.dll(0x00007FFE1C770000) + 0x35B755 byte(s), fl::ChatSession::ProcessRequestImpl() + 0x825 byte(s), C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\src\inferencing\generative\chat\chat_session.cc, line 1671 + 0x0 byte(s)
0x00007FFE1CA63DA8, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\build\Windows\RelWithDebInfo\bin\RelWithDebInfo\foundry_local.dll(0x00007FFE1C770000) + 0x2F3DA8 byte(s), fl::Session::ProcessRequest() + 0x488 byte(s), C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\src\inferencing\session\session.cc, line 290 + 0x0 byte(s)
0x00007FFE1C90D791, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\build\Windows\RelWithDebInfo\bin\RelWithDebInfo\foundry_local.dll(0x00007FFE1C770000) + 0x19D791 byte(s), fl::api::`anonymous namespace'::EmbeddedSession::ProcessRequest() + 0x61 byte(s), C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\src\api\embedded_backend.cc, line 47 + 0x47 byte(s)
0x00007FFE1C8EE711, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\build\Windows\RelWithDebInfo\bin\RelWithDebInfo\foundry_local.dll(0x00007FFE1C770000) + 0x17E711 byte(s), Session_ProcessRequestImpl() + 0xB1 byte(s), C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\foundry-local\sdk_v2\cpp\src\c_api.cc, line 1902 + 0x20 byte(s)
0x00007FFEE64010F3, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\_cffi_backend.cp312-win_amd64.pyd(0x00007FFEE6400000) + 0x10F3 byte(s)
0x00007FFEE641A64C, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\_cffi_backend.cp312-win_amd64.pyd(0x00007FFEE6400000) + 0x1A64C byte(s), PyInit__cffi_backend() + 0x73C byte(s)
0x00007FFEE640771F, C:\Users\prathikrao\OneDrive - Microsoft\Desktop\foundry-local\.venv312\Lib\site-packages\_cffi_backend.cp312-win_amd64.pyd(0x00007FFEE6400000) + 0x771F byte(s)
0x00007FFE35AF2018, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0x82018 byte(s), PyObject_Vectorcall() + 0x688 byte(s)
0x00007FFE35AF19C5, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0x819C5 byte(s), PyObject_Vectorcall() + 0x35 byte(s)
0x00007FFE35AF2EA5, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0x82EA5 byte(s), _PyEval_EvalFrameDefault() + 0x895 byte(s)
0x00007FFE35AA81E4, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0x381E4 byte(s), _PyObject_ClearManagedDict() + 0x384 byte(s)
0x00007FFE35AA6B66, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0x36B66 byte(s), PyEval_EvalCode() + 0xB6 byte(s)
0x00007FFE35B5E838, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0xEE838 byte(s), _Py_SourceAsString() + 0x90C byte(s)
0x00007FFE35B5EA70, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0xEEA70 byte(s), _PyModule_ClearDict() + 0x1FC byte(s)
0x00007FFE35B3A5D4, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0xCA5D4 byte(s), PyDict_DelItemString() + 0xFC byte(s)
0x00007FFE35B3A432, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0xCA432 byte(s), _PyRun_SimpleFileObject() + 0x126 byte(s)
0x00007FFE35B3CD19, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0xCCD19 byte(s), _PyRun_AnyFileObject() + 0x4D byte(s)
0x00007FFE35B3CEEA, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0xCCEEA byte(s), _PyEval_MakePendingCalls() + 0x11A byte(s)
0x00007FFE35B3CBEB, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0xCCBEB byte(s), PyErr_SetExcFromWindowsErrWithFilenameObjects() + 0x263 byte(s)
0x00007FFE35A98F1B, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0x28F1B byte(s), PyMem_GetAllocator() + 0x5FF byte(s)
0x00007FFE35A98700, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0x28700 byte(s), Py_RunMain() + 0x18 byte(s)
0x00007FFE35A986E3, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python312.dll(0x00007FFE35A70000) + 0x286E3 byte(s), Py_Main() + 0x2B byte(s)
0x00007FF6F2991230, C:\Users\prathikrao\AppData\Local\Programs\Python\Python312\python.exe(0x00007FF6F2990000) + 0x1230 byte(s)
0x00007FFF03FEDDA7, C:\WINDOWS\System32\KERNEL32.DLL(0x00007FFF03FC0000) + 0x2DDA7 byte(s), BaseThreadInitThunk() + 0x17 byte(s)
0x00007FFF0507EE4C, C:\WINDOWS\SYSTEM32\ntdll.dll(0x00007FFF05000000) + 0x7EE4C byte(s), RtlUserThreadStart() + 0x2C byte(s)

```
