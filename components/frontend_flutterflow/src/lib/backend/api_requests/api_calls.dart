import 'dart:convert';
import 'dart:typed_data';

import '../../flutter_flow/flutter_flow_util.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'api_manager.dart';

export 'api_manager.dart' show ApiCallResponse;

const _kPrivateApiFunctionName = 'ffPrivateApiCall';


/// Start Google CLP Authorization Group Code

class GoogleCLPAuthorizationGroup {
  static String? baseUrl = dotenv.env['API_BASE_URL'];
  static Map<String, String> headers = {};
  static SignInCall signInCall = SignInCall();
  static SignUpCall signUpCall = SignUpCall();
  static CreateUserCall createUserCall = CreateUserCall();
  static RefreshSessionCall refreshSessionCall = RefreshSessionCall();
}

class SignInCall {
  Future<ApiCallResponse> call({
    String? email = '',
    String? password = '',
  }) {
    final body = '''
{
  "email": "${email}",
  "password": "${password}"
}''';
    return ApiManager.instance.makeApiCall(
      callName: 'Sign In',
      apiUrl:
          '${GoogleCLPAuthorizationGroup.baseUrl}/authentication/api/v1/sign-in/credentials',
      callType: ApiCallType.POST,
      headers: {
        ...GoogleCLPAuthorizationGroup.headers,
      },
      params: {},
      body: body,
      bodyType: BodyType.JSON,
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic token(dynamic response) => getJsonField(
        response,
        r'''$.data.idToken''',
      );
  dynamic refreshToken(dynamic response) => getJsonField(
        response,
        r'''$.data.refreshToken''',
      );
  dynamic userID(dynamic response) => getJsonField(
        response,
        r'''$.data.user_id''',
      );
  dynamic sessionID(dynamic response) => getJsonField(
        response,
        r'''$.data.session_id''',
      );
  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
}

class SignUpCall {
  Future<ApiCallResponse> call({
    String? email = '',
    String? password = '',
  }) {
    final body = '''
{
  "email": "${email}",
  "password": "${password}"
}''';
    return ApiManager.instance.makeApiCall(
      callName: 'Sign Up',
      apiUrl:
          '${GoogleCLPAuthorizationGroup.baseUrl}/authentication/api/v1/sign-up/credentials',
      callType: ApiCallType.POST,
      headers: {
        ...GoogleCLPAuthorizationGroup.headers,
      },
      params: {},
      body: body,
      bodyType: BodyType.JSON,
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
}

class CreateUserCall {
  Future<ApiCallResponse> call({
    String? firstName = '',
    String? lastName = '',
    String? email = '',
    String? cLPToken = '',
  }) {
    final body = '''
{
  "first_name": "${firstName}",
  "last_name": "${lastName}",
  "email": "${email}",
  "user_type": "learner",
  "status": "active",
  "is_registered": "true",
  "failed_login_attempts_count": 0,
  "access_api_docs": "true"
}''';
    return ApiManager.instance.makeApiCall(
      callName: 'Create User',
      apiUrl:
          '${GoogleCLPAuthorizationGroup.baseUrl}/user-management/api/v1/user',
      callType: ApiCallType.POST,
      headers: {
        ...GoogleCLPAuthorizationGroup.headers,
        'Authorization': 'Bearer ${cLPToken}',
      },
      params: {},
      body: body,
      bodyType: BodyType.JSON,
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
}

class RefreshSessionCall {
  Future<ApiCallResponse> call({
    String? refreshToken = '',
  }) {
    final body = '''
{
  "refresh_token": "${refreshToken}"
}''';
    return ApiManager.instance.makeApiCall(
      callName: 'Refresh Session',
      apiUrl:
          '${GoogleCLPAuthorizationGroup.baseUrl}/authentication/api/v1/generate',
      callType: ApiCallType.POST,
      headers: {
        ...GoogleCLPAuthorizationGroup.headers,
      },
      params: {},
      body: body,
      bodyType: BodyType.JSON,
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic token(dynamic response) => getJsonField(
        response,
        r'''$.data.access_token''',
      );
  dynamic refreshToken(dynamic response) => getJsonField(
        response,
        r'''$.data.refresh_token''',
      );
  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
}

/// End Google CLP Authorization Group Code

/// Start Google CLP Chat Group Code

class GoogleCLPChatGroup {
  static String? baseUrl = dotenv.env['API_BASE_URL'];
  static Map<String, String> headers = {};
  static GetModelsCall getModelsCall = GetModelsCall();
  static CreateChatCall createChatCall = CreateChatCall();
  static UpdateTitleCall updateTitleCall = UpdateTitleCall();
  static GenerateResponseCall generateResponseCall = GenerateResponseCall();
  static GenerateSingleResponseCall generateSingleResponseCall =
      GenerateSingleResponseCall();
  static GetChatCall getChatCall = GetChatCall();
  static GetAllChatsCall getAllChatsCall = GetAllChatsCall();
  static DeleteChatCall deleteChatCall = DeleteChatCall();
}

class GetModelsCall {
  Future<ApiCallResponse> call({
    String? token = '',
  }) {
    return ApiManager.instance.makeApiCall(
      callName: 'Get Models',
      apiUrl: '${GoogleCLPChatGroup.baseUrl}/llm-service/api/v1/llm',
      callType: ApiCallType.GET,
      headers: {
        ...GoogleCLPChatGroup.headers,
        'Authorization': 'Bearer ${token}',
      },
      params: {},
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic models(dynamic response) => getJsonField(
        response,
        r'''$.data''',
        true,
      );
  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
}

class CreateChatCall {
  Future<ApiCallResponse> call({
    String? token = '',
    String? model = '',
    String? prompt = '',
  }) {
    final body = '''
{
  "prompt": "${prompt}",
  "llm_type": "${model}"
}''';
    return ApiManager.instance.makeApiCall(
      callName: 'Create Chat',
      apiUrl: '${GoogleCLPChatGroup.baseUrl}/llm-service/api/v1/chat',
      callType: ApiCallType.POST,
      headers: {
        ...GoogleCLPChatGroup.headers,
        'Authorization': 'Bearer ${token}',
      },
      params: {},
      body: body,
      bodyType: BodyType.JSON,
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic messages(dynamic response) => getJsonField(
        response,
        r'''$.data.history''',
        true,
      );
  dynamic timestamp(dynamic response) => getJsonField(
        response,
        r'''$.data.last_modified_time''',
      );
  dynamic id(dynamic response) => getJsonField(
        response,
        r'''$.data.id''',
      );
  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
}

class UpdateTitleCall {
  Future<ApiCallResponse> call({
    String? token = '',
    String? title = '',
    String? chatID = '',
  }) {
    final body = '''
{
  "title": "${title}"
}''';
    return ApiManager.instance.makeApiCall(
      callName: 'Update Title',
      apiUrl: '${GoogleCLPChatGroup.baseUrl}/llm-service/api/v1/chat/${chatID}',
      callType: ApiCallType.PUT,
      headers: {
        ...GoogleCLPChatGroup.headers,
        'Authorization': 'Bearer ${token}',
      },
      params: {},
      body: body,
      bodyType: BodyType.JSON,
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
}

class GenerateResponseCall {
  Future<ApiCallResponse> call({
    String? token = '',
    String? prompt = '',
    String? model = '',
    String? chatID = '',
  }) {
    final body = '''
{
  "prompt": "${prompt}",
  "llm_type": "${model}"
}''';
    return ApiManager.instance.makeApiCall(
      callName: 'Generate Response',
      apiUrl:
          '${GoogleCLPChatGroup.baseUrl}/llm-service/api/v1/chat/${chatID}/generate',
      callType: ApiCallType.POST,
      headers: {
        ...GoogleCLPChatGroup.headers,
        'Authorization': 'Bearer ${token}',
      },
      params: {},
      body: body,
      bodyType: BodyType.JSON,
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic messagesRoot(dynamic response) => getJsonField(
        response,
        r'''$.data.history''',
        true,
      );
  dynamic datetime(dynamic response) => getJsonField(
        response,
        r'''$.data.last_modified_time''',
      );
  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
  dynamic userMessages(dynamic response) => getJsonField(
        response,
        r'''$.data.history[:].HumanInput''',
        true,
      );
  dynamic model(dynamic response) => getJsonField(
        response,
        r'''$.data.llm_type''',
      );
  dynamic chatID(dynamic response) => getJsonField(
        response,
        r'''$.data.id''',
      );
  dynamic aIMessages(dynamic response) => getJsonField(
        response,
        r'''$.data.history[:].AIOutput''',
        true,
      );
}

class GenerateSingleResponseCall {
  Future<ApiCallResponse> call({
    String? token = '',
    String? prompt = '',
  }) {
    final body = '''
{
  "prompt": "${prompt}"
}''';
    return ApiManager.instance.makeApiCall(
      callName: 'Generate Single Response',
      apiUrl: '${GoogleCLPChatGroup.baseUrl}/llm-service/api/v1/llm/generate',
      callType: ApiCallType.POST,
      headers: {
        ...GoogleCLPChatGroup.headers,
        'Authorization': 'Bearer ${token}',
      },
      params: {},
      body: body,
      bodyType: BodyType.JSON,
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic message(dynamic response) => getJsonField(
        response,
        r'''$.content''',
      );
  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
}

class GetChatCall {
  Future<ApiCallResponse> call({
    String? token = '',
    String? chatID = '',
  }) {
    return ApiManager.instance.makeApiCall(
      callName: 'Get Chat',
      apiUrl: '${GoogleCLPChatGroup.baseUrl}/llm-service/api/v1/chat/${chatID}',
      callType: ApiCallType.GET,
      headers: {
        ...GoogleCLPChatGroup.headers,
        'Authorization': 'Bearer ${token}',
      },
      params: {},
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic messages(dynamic response) => getJsonField(
        response,
        r'''$.data.history''',
        true,
      );
  dynamic title(dynamic response) => getJsonField(
        response,
        r'''$.data.title''',
      );
  dynamic datetime(dynamic response) => getJsonField(
        response,
        r'''$.data.last_modified_time''',
      );
  dynamic model(dynamic response) => getJsonField(
        response,
        r'''$.data.llm_type''',
      );
  dynamic id(dynamic response) => getJsonField(
        response,
        r'''$.data.id''',
      );
  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
  dynamic userMessages(dynamic response) => getJsonField(
        response,
        r'''$.data.history[:].HumanInput''',
        true,
      );
  dynamic aIMessages(dynamic response) => getJsonField(
        response,
        r'''$.data.history[:].AIOutput''',
        true,
      );
}

class GetAllChatsCall {
  Future<ApiCallResponse> call({
    String? token = '',
  }) {
    return ApiManager.instance.makeApiCall(
      callName: 'Get All Chats',
      apiUrl: '${GoogleCLPChatGroup.baseUrl}/llm-service/api/v1/chat',
      callType: ApiCallType.GET,
      headers: {
        ...GoogleCLPChatGroup.headers,
        'Authorization': 'Bearer ${token}',
      },
      params: {},
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic id(dynamic response) => getJsonField(
        response,
        r'''$.data[:].id''',
        true,
      );
  dynamic model(dynamic response) => getJsonField(
        response,
        r'''$.data[:].llm_type''',
        true,
      );
  dynamic title(dynamic response) => getJsonField(
        response,
        r'''$.data[:].title''',
        true,
      );
  dynamic datetime(dynamic response) => getJsonField(
        response,
        r'''$.data[:].last_modified_time''',
        true,
      );
  dynamic messages(dynamic response) => getJsonField(
        response,
        r'''$.data[:].history''',
        true,
      );
  dynamic root(dynamic response) => getJsonField(
        response,
        r'''$.data[:]''',
        true,
      );
  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
}

class DeleteChatCall {
  Future<ApiCallResponse> call({
    String? chatID = '',
    String? token = '',
  }) {
    return ApiManager.instance.makeApiCall(
      callName: 'Delete Chat',
      apiUrl: '${GoogleCLPChatGroup.baseUrl}/llm-service/api/v1/chat/${chatID}',
      callType: ApiCallType.DELETE,
      headers: {
        ...GoogleCLPChatGroup.headers,
        'Authorization': 'Bearer ${token}',
      },
      params: {},
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
}

/// End Google CLP Chat Group Code

/// Start Google CLP Document Query Group Code

class GoogleCLPDocumentQueryGroup {
  static String? baseUrl = dotenv.env['API_BASE_URL'];
  static Map<String, String> headers = {};
  static GetEnginesCall getEnginesCall = GetEnginesCall();
  static MakeQueryCall makeQueryCall = MakeQueryCall();
  static ContinueQueryCall continueQueryCall = ContinueQueryCall();
  static GetUserQueryHistoryCall getUserQueryHistoryCall =
      GetUserQueryHistoryCall();
}

class GetEnginesCall {
  Future<ApiCallResponse> call({
    String? token = '',
  }) {
    return ApiManager.instance.makeApiCall(
      callName: 'Get Engines',
      apiUrl: '${GoogleCLPDocumentQueryGroup.baseUrl}/llm-service/api/v1/query',
      callType: ApiCallType.GET,
      headers: {
        ...GoogleCLPDocumentQueryGroup.headers,
        'Authorization': 'Bearer ${token}',
      },
      params: {},
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
  dynamic engines(dynamic response) => getJsonField(
        response,
        r'''$.data[:].name''',
        true,
      );
  dynamic engineIds(dynamic response) => getJsonField(
        response,
        r'''$.data[:].id''',
        true,
      );
}

class MakeQueryCall {
  Future<ApiCallResponse> call({
    String? token = '',
    String? prompt = '',
    String? qEngineId = '',
  }) {
    final body = '''
{
  "prompt": "${prompt}"
}''';
    return ApiManager.instance.makeApiCall(
      callName: 'Make Query',
      apiUrl:
          '${GoogleCLPDocumentQueryGroup.baseUrl}/llm-service/api/v1/query/engine/${qEngineId}',
      callType: ApiCallType.POST,
      headers: {
        ...GoogleCLPDocumentQueryGroup.headers,
        'Authorization': 'Bearer ${token}',
      },
      params: {},
      body: body,
      bodyType: BodyType.JSON,
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
  dynamic queryResultRoot(dynamic response) => getJsonField(
        response,
        r'''$.data.query_result''',
      );
  dynamic queryRefsRoot(dynamic response) => getJsonField(
        response,
        r'''$.data.query_references''',
        true,
      );
  dynamic queryResponse(dynamic response) => getJsonField(
        response,
        r'''$.data.query_result.response''',
      );
  dynamic refTexts(dynamic response) => getJsonField(
        response,
        r'''$.data.query_references[:].document_text''',
        true,
      );
  dynamic refUrls(dynamic response) => getJsonField(
        response,
        r'''$.data.query_references[:].document_url''',
        true,
      );
  dynamic queryDatetime(dynamic response) => getJsonField(
        response,
        r'''$.data.query_result.last_modified_time''',
      );
}

class ContinueQueryCall {
  Future<ApiCallResponse> call({
    String? token = '',
    String? queryId = '',
  }) {
    return ApiManager.instance.makeApiCall(
      callName: 'Continue Query',
      apiUrl:
          '${GoogleCLPDocumentQueryGroup.baseUrl}/llm-service/api/v1/query/${queryId}',
      callType: ApiCallType.POST,
      headers: {
        ...GoogleCLPDocumentQueryGroup.headers,
        'Authorization': 'Bearer ${token}',
      },
      params: {},
      bodyType: BodyType.JSON,
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic apiMessage(dynamic response) => getJsonField(
        response,
        r'''$.message''',
      );
}

class GetUserQueryHistoryCall {
  Future<ApiCallResponse> call({
    String? userId = '',
    String? token = '',
  }) {
    return ApiManager.instance.makeApiCall(
      callName: 'Get User Query History',
      apiUrl:
          '${GoogleCLPDocumentQueryGroup.baseUrl}/llm-service/api/v1/query/user/${userId}',
      callType: ApiCallType.GET,
      headers: {
        ...GoogleCLPDocumentQueryGroup.headers,
        'Authorization': 'Bearer ${token}',
      },
      params: {},
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
    );
  }

  dynamic dateTime(dynamic response) => getJsonField(
        response,
        r'''$.data[:].lastModifiedBy''',
        true,
      );
}

/// End Google CLP Document Query Group Code

class ApiPagingParams {
  int nextPageNumber = 0;
  int numItems = 0;
  dynamic lastResponse;

  ApiPagingParams({
    required this.nextPageNumber,
    required this.numItems,
    required this.lastResponse,
  });

  @override
  String toString() =>
      'PagingParams(nextPageNumber: $nextPageNumber, numItems: $numItems, lastResponse: $lastResponse,)';
}

String _serializeList(List? list) {
  list ??= <String>[];
  try {
    return json.encode(list);
  } catch (_) {
    return '[]';
  }
}

String _serializeJson(dynamic jsonVar, [bool isList = false]) {
  jsonVar ??= (isList ? [] : {});
  try {
    return json.encode(jsonVar);
  } catch (_) {
    return isList ? '[]' : '{}';
  }
}
