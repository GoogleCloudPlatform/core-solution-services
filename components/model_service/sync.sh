#!/bin/bash
cp $BASE_DIR/components/llm_service/requirements.txt $BASE_DIR/components/model_service/
cp $BASE_DIR/components/llm_service/requirements-test.txt $BASE_DIR/components/model_service/
cp -r $BASE_DIR/components/llm_service/src/services/* $BASE_DIR/components/model_service/src/services
cp $BASE_DIR/components/llm_service/src/routes/llm.py $BASE_DIR/components/model_service/src/routes
cp $BASE_DIR/components/llm_service/src/routes/llm_test.py $BASE_DIR/components/model_service/src/routes
cp -r $BASE_DIR/components/llm_service/src/config $BASE_DIR/components/model_service/src
cp -r $BASE_DIR/components/llm_service/src/schemas $BASE_DIR/components/model_service/src
cp -r $BASE_DIR/components/llm_service/kustomize $BASE_DIR/components/model_service/
