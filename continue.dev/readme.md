```
pip install uvicorn fastapi pydantic-settings sse-starlette starlette-context PyYAML
pip install scikit-build mistral-common

cd vendor/
rm -rf llama.cpp/
git clone https://github.com/ggerganov/llama.cpp.git

cd ..

export CMAKE_ARGS="-DLLAMA_CUBLAS=on -DCMAKE_BUILD_TYPE=Debug"
pip install -e .

```