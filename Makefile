OPENAPI_FILE := openapi/openapi.yaml
OUTPUT_DIR_OA := generated/openapi
PROTO_FILE := proto/medication.proto
OUTPUT_DIR_GRPC := generated/grpc

start:
	uvicorn intern_engine.main:app --reload

lint:
	uv run flake8

generategrpc:
	python -m grpc_tools.protoc \
	-Iproto \
	--python_out=$(OUTPUT_DIR_GRPC) \
	--grpc_python_out=$(OUTPUT_DIR_GRPC) \
	$(PROTO_FILE) 


generateoa:
	rm -rf $(OUTPUT_DIR)
	openapi-python-client generate --path $(OPENAPI_FILE) --output-path $(OUTPUT_DIR_OA)
