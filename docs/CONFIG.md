# LLMService Model config

Model config is handled by the `config.ModelConfig` class. Instances of this class represent config for LLM models managed by the LLM Service.  Config is stored in this class in four instance dicts, representing config for model providers, model vendors, LLM models, and embedding models.

## Provider config
```
llm_model_providers: Dict[str, Dict[str, Any]]
  { ...
    provider_id: {
      {
        ...
        provider config key: value
      }
  }
```

Provider config keys:
- *enabled*: is provider enabled
- *env_flag*: environment variable to enable/disable provider
- *model_params*: global provider generation parameters


## Vendor config

```
llm_model_vendors: Dict[str, Dict[str, Any]]
  { ...
    vendor_id: {
      ...
      vendor config key: value
    }
  }
```

Vendor config keys:
- *enabled*: is vendor enabled
- *env_flag*: environment variable to enable/disable vendor
- *api_key*: secret id for api key
- *model_params*: global vendor generation parameters

## Model config

```
llm_models: Dict[str, Dict[str, Any]]
  { ...
    model_id: {
      ...
      model config key: value
    }
  }
```

Model config keys:
- *enabled*: is model enabled
- *is_chat*: is the model a chat model
- *provider*: the provider of the model
- *model_endpoint*: base url of a model served by an external provider
- *model_class*: class to instantiate for model, e.g. langchain model class
- *model_params*: generation parameters
- *vendor*: vendor id
- *env_flag*: environment variable to enable/disable model
- *model_file_url*: url of model file to load

## Embedding model config
 
```
llm_embedding_models: Dict[str, Dict[str, Any]]
  { ...
    model_id: {
      ...
      embedding model config key: value
    }
  }
```

Embedding model config uses all model config keys except *is_chat*

Embedding models also include these keys:
- *dimension*: dimension of embedding vector
