import '/backend/api_requests/api_calls.dart';
import '/components/chat_bubbles/chat_bubbles_widget.dart';
import '/components/edit_chat_modal/edit_chat_modal_widget.dart';
import '/components/logo_header/logo_header_widget.dart';
import '/components/side_menu/side_menu_widget.dart';
import '/flutter_flow/flutter_flow_animations.dart';
import '/flutter_flow/flutter_flow_icon_button.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import '/flutter_flow/custom_functions.dart' as functions;
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lottie/lottie.dart';
import 'package:provider/provider.dart';
import 'chat_model.dart';
export 'chat_model.dart';

class ChatWidget extends StatefulWidget {
  const ChatWidget({
    Key? key,
    required this.chatRef,
  }) : super(key: key);

  final String? chatRef;

  @override
  _ChatWidgetState createState() => _ChatWidgetState();
}

class _ChatWidgetState extends State<ChatWidget> with TickerProviderStateMixin {
  late ChatModel _model;

  final scaffoldKey = GlobalKey<ScaffoldState>();

  final animationsMap = {
    'chatBubblesOnActionTriggerAnimation': AnimationInfo(
      trigger: AnimationTrigger.onActionTrigger,
      applyInitialState: true,
      effects: [
        MoveEffect(
          curve: Curves.easeInOut,
          delay: 0.ms,
          duration: 530.ms,
          begin: Offset(0.0, 19.0),
          end: Offset(0.0, 0.0),
        ),
      ],
    ),
  };

  @override
  void initState() {
    super.initState();
    _model = createModel(context, () => ChatModel());

    // On page load action.
    SchedulerBinding.instance.addPostFrameCallback((_) async {
      FFAppState().update(() {
        FFAppState().pageSelected = 2;
      });
    });

    _model.promptController ??= TextEditingController();
    setupAnimations(
      animationsMap.values.where((anim) =>
          anim.trigger == AnimationTrigger.onActionTrigger ||
          !anim.applyInitialState),
      this,
    );

    WidgetsBinding.instance.addPostFrameCallback((_) => setState(() {}));
  }

  @override
  void dispose() {
    _model.dispose();

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    context.watch<FFAppState>();

    return FutureBuilder<ApiCallResponse>(
      future: GoogleCLPChatGroup.getChatCall.call(
        token: FFAppState().token,
        chatID: widget.chatRef,
      ),
      builder: (context, snapshot) {
        // Customize what your widget looks like when it's loading.
        if (!snapshot.hasData) {
          return Scaffold(
            backgroundColor: FlutterFlowTheme.of(context).primaryBackground,
            body: Center(
              child: SizedBox(
                width: 50.0,
                height: 50.0,
                child: CircularProgressIndicator(
                  color: FlutterFlowTheme.of(context).primary,
                ),
              ),
            ),
          );
        }
        final chatGetChatResponse = snapshot.data!;
        return GestureDetector(
          onTap: () => FocusScope.of(context).requestFocus(_model.unfocusNode),
          child: Scaffold(
            key: scaffoldKey,
            backgroundColor: FlutterFlowTheme.of(context).primaryBackground,
            drawer: Container(
              width: 275.0,
              child: Drawer(
                elevation: 16.0,
                child: Container(
                  width: double.infinity,
                  height: double.infinity,
                  decoration: BoxDecoration(
                    color: Color(0x2D4490DB),
                  ),
                  child: wrapWithModel(
                    model: _model.sideMenuModel,
                    updateCallback: () => setState(() {}),
                    child: SideMenuWidget(
                      currentChatRef: widget.chatRef,
                    ),
                  ),
                ),
              ),
            ),
            body: SafeArea(
              top: true,
              child: Container(
                width: double.infinity,
                height: double.infinity,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Color(0xFFf0f4f9), Color(0xFFf0f4f9)],
                    stops: [0.0, 1.0],
                    begin: AlignmentDirectional(-0.64, 1.0),
                    end: AlignmentDirectional(0.64, -1.0),
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding:
                          EdgeInsetsDirectional.fromSTEB(16.0, 16.0, 0.0, 0.0),
                      child: InkWell(
                        splashColor: Colors.transparent,
                        focusColor: Colors.transparent,
                        hoverColor: Colors.transparent,
                        highlightColor: Colors.transparent,
                        onTap: () async {
                          context.pushNamed('Landing');
                        },
                        child: wrapWithModel(
                          model: _model.logoHeaderModel,
                          updateCallback: () => setState(() {}),
                          child: LogoHeaderWidget(),
                        ),
                      ),
                    ),
                    Expanded(
                      child: Align(
                        alignment: AlignmentDirectional(0.0, 0.0),
                        child: Container(
                          width: double.infinity,
                          height: double.infinity,
                          constraints: BoxConstraints(
                            maxWidth: 1200.0,
                          ),
                          decoration: BoxDecoration(),
                          child: Padding(
                            padding: EdgeInsetsDirectional.fromSTEB(
                                15.0, 0.0, 15.0, 0.0),
                            child: Row(
                              mainAxisSize: MainAxisSize.max,
                              children: [
                                Expanded(
                                  child: Padding(
                                    padding: EdgeInsetsDirectional.fromSTEB(
                                        0.0, 30.0, 0.0, 30.0),
                                    child: Container(
                                      width: double.infinity,
                                      height: double.infinity,
                                      decoration: BoxDecoration(),
                                      child: Column(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          Expanded(
                                            child: Row(
                                              mainAxisSize: MainAxisSize.max,
                                              children: [
                                                Expanded(
                                                  child: Container(
                                                    width: double.infinity,
                                                    height: double.infinity,
                                                    decoration: BoxDecoration(
                                                      boxShadow: [
                                                        BoxShadow(
                                                          blurRadius: 5.0,
                                                          color:
                                                              Color(0x00FFFFFF),
                                                          offset:
                                                              Offset(1.0, 2.0),
                                                        )
                                                      ],
                                                      gradient: LinearGradient(
                                                        colors: [
                                                          Color(0xFFFFFFFF),
                                                          Color(0xFFFFFFFF)
                                                        ],
                                                        stops: [0.0, 1.0],
                                                        begin:
                                                            AlignmentDirectional(
                                                                -0.64, 1.0),
                                                        end:
                                                            AlignmentDirectional(
                                                                0.64, -1.0),
                                                      ),
                                                      borderRadius:
                                                          BorderRadius.circular(
                                                              15.0),
                                                      border: Border.all(
                                                        color:
                                                            Color(0x37FFFFFF),
                                                      ),
                                                    ),
                                                    child: Column(
                                                      mainAxisSize:
                                                          MainAxisSize.max,
                                                      mainAxisAlignment:
                                                          MainAxisAlignment
                                                              .center,
                                                      children: [
                                                        Padding(
                                                          padding:
                                                              EdgeInsetsDirectional
                                                                  .fromSTEB(
                                                                      10.0,
                                                                      6.0,
                                                                      10.0,
                                                                      0.0),
                                                          child: Row(
                                                            mainAxisSize:
                                                                MainAxisSize
                                                                    .max,
                                                            mainAxisAlignment:
                                                                MainAxisAlignment
                                                                    .spaceBetween,
                                                            children: [
                                                              if (FFAppState()
                                                                      .pageSelected !=
                                                                  1)
                                                                FlutterFlowIconButton(
                                                                  borderColor:
                                                                      Color(
                                                                          0x004490DB),
                                                                  borderRadius:
                                                                      10.0,
                                                                  borderWidth:
                                                                      1.0,
                                                                  buttonSize:
                                                                      40.0,
                                                                  hoverColor:
                                                                      FlutterFlowTheme.of(
                                                                              context)
                                                                          .primary,
                                                                  hoverIconColor:
                                                                      Colors
                                                                          .white,
                                                                  icon: Icon(
                                                                    Icons
                                                                        .menu_rounded,
                                                                    color: Color(
                                                                        0xFF969DA9),
                                                                    size: 17.0,
                                                                  ),
                                                                  onPressed:
                                                                      () async {
                                                                    scaffoldKey
                                                                        .currentState!
                                                                        .openDrawer();
                                                                  },
                                                                ),
                                                              Text(
                                                                valueOrDefault<
                                                                    String>(
                                                                  GoogleCLPChatGroup
                                                                      .getChatCall
                                                                      .title(
                                                                        chatGetChatResponse
                                                                            .jsonBody,
                                                                      )
                                                                      .toString(),
                                                                  'New Chat',
                                                                ),
                                                                style: FlutterFlowTheme.of(
                                                                        context)
                                                                    .bodyMedium
                                                                    .override(
                                                                      fontFamily:
                                                                          'Poppins',
                                                                      color: FlutterFlowTheme.of(
                                                                              context)
                                                                          .secondaryText,
                                                                      fontSize:
                                                                          12.0,
                                                                    ),
                                                              ),
                                                              if (FFAppState()
                                                                      .pageSelected !=
                                                                  1)
                                                                FlutterFlowIconButton(
                                                                  borderColor:
                                                                      Color(
                                                                          0x004490DB),
                                                                  borderRadius:
                                                                      10.0,
                                                                  borderWidth:
                                                                      1.0,
                                                                  buttonSize:
                                                                      40.0,
                                                                  hoverColor:
                                                                      FlutterFlowTheme.of(
                                                                              context)
                                                                          .primary,
                                                                  hoverIconColor:
                                                                      Colors
                                                                          .white,
                                                                  icon: FaIcon(
                                                                    FontAwesomeIcons
                                                                        .edit,
                                                                    color: Color(
                                                                        0xFF969DA9),
                                                                    size: 15.0,
                                                                  ),
                                                                  onPressed:
                                                                      () async {
                                                                    await showModalBottomSheet(
                                                                      isScrollControlled:
                                                                          true,
                                                                      backgroundColor:
                                                                          Colors
                                                                              .transparent,
                                                                      enableDrag:
                                                                          false,
                                                                      context:
                                                                          context,
                                                                      builder:
                                                                          (context) {
                                                                        return GestureDetector(
                                                                          onTap: () =>
                                                                              FocusScope.of(context).requestFocus(_model.unfocusNode),
                                                                          child:
                                                                              Padding(
                                                                            padding:
                                                                                MediaQuery.viewInsetsOf(context),
                                                                            child:
                                                                                EditChatModalWidget(
                                                                              chartTitle: valueOrDefault<String>(
                                                                                GoogleCLPChatGroup.getChatCall
                                                                                    .title(
                                                                                      chatGetChatResponse.jsonBody,
                                                                                    )
                                                                                    .toString(),
                                                                                'New Chat',
                                                                              ),
                                                                              chatRef: widget.chatRef,
                                                                            ),
                                                                          ),
                                                                        );
                                                                      },
                                                                    ).then((value) =>
                                                                        setState(
                                                                            () {}));
                                                                  },
                                                                ),
                                                            ],
                                                          ),
                                                        ),
                                                        Expanded(
                                                          child: Padding(
                                                            padding:
                                                                EdgeInsetsDirectional
                                                                    .fromSTEB(
                                                                        10.0,
                                                                        10.0,
                                                                        10.0,
                                                                        0.0),
                                                            child: Container(
                                                              width: double
                                                                  .infinity,
                                                              height: double
                                                                  .infinity,
                                                              constraints:
                                                                  BoxConstraints(
                                                                maxWidth: 720.0,
                                                              ),
                                                              decoration:
                                                                  BoxDecoration(),
                                                              child: Builder(
                                                                builder:
                                                                    (context) {
                                                                  final message = functions
                                                                          .reverseOrder(GoogleCLPChatGroup.getChatCall
                                                                              .messages(
                                                                                chatGetChatResponse.jsonBody,
                                                                              )
                                                                              ?.toList())
                                                                          ?.toList() ??
                                                                      [];
                                                                  if (message
                                                                      .isEmpty) {
                                                                    return Center(
                                                                      child: Image
                                                                          .asset(
                                                                        'assets/images/bardStars.png',
                                                                        width:
                                                                            100.0,
                                                                        height:
                                                                            100.0,
                                                                      ),
                                                                    );
                                                                  }
                                                                  return ListView
                                                                      .builder(
                                                                    padding:
                                                                        EdgeInsets
                                                                            .zero,
                                                                    reverse:
                                                                        true,
                                                                    shrinkWrap:
                                                                        true,
                                                                    scrollDirection:
                                                                        Axis.vertical,
                                                                    itemCount:
                                                                        message
                                                                            .length,
                                                                    itemBuilder:
                                                                        (context,
                                                                            messageIndex) {
                                                                      final messageItem =
                                                                          message[
                                                                              messageIndex];
                                                                      return ChatBubblesWidget(
                                                                        key: Key(
                                                                            'Key5t3_${messageIndex}_of_${message.length}'),
                                                                        humanMessage:
                                                                            getJsonField(
                                                                          messageItem,
                                                                          r'''$.HumanInput''',
                                                                        ).toString(),
                                                                        aiMessage:
                                                                            getJsonField(
                                                                          messageItem,
                                                                          r'''$.AIOutput''',
                                                                        ).toString(),
                                                                        human: getJsonField(
                                                                              messageItem,
                                                                              r'''$.HumanInput''',
                                                                            ) !=
                                                                            null,
                                                                        ai: getJsonField(
                                                                              messageItem,
                                                                              r'''$.AIOutput''',
                                                                            ) !=
                                                                            null,
                                                                      ).animateOnActionTrigger(
                                                                        animationsMap[
                                                                            'chatBubblesOnActionTriggerAnimation']!,
                                                                      );
                                                                    },
                                                                  );
                                                                },
                                                              ),
                                                            ),
                                                          ),
                                                        ),
                                                        if (FFAppState()
                                                                .awaitingReply ==
                                                            true)
                                                          Column(
                                                            mainAxisSize:
                                                                MainAxisSize
                                                                    .max,
                                                            children: [
                                                              Container(
                                                                width: double
                                                                    .infinity,
                                                                constraints:
                                                                    BoxConstraints(
                                                                  maxWidth:
                                                                      720.0,
                                                                ),
                                                                decoration:
                                                                    BoxDecoration(),
                                                                child: Padding(
                                                                  padding: EdgeInsetsDirectional
                                                                      .fromSTEB(
                                                                          0.0,
                                                                          15.0,
                                                                          0.0,
                                                                          5.0),
                                                                  child: Row(
                                                                    mainAxisSize:
                                                                        MainAxisSize
                                                                            .max,
                                                                    crossAxisAlignment:
                                                                        CrossAxisAlignment
                                                                            .start,
                                                                    children: [
                                                                      Expanded(
                                                                        flex: 1,
                                                                        child:
                                                                            Container(
                                                                          width:
                                                                              100.0,
                                                                          height:
                                                                              20.0,
                                                                          decoration:
                                                                              BoxDecoration(),
                                                                        ),
                                                                      ),
                                                                      Expanded(
                                                                        flex: 4,
                                                                        child:
                                                                            Row(
                                                                          mainAxisSize:
                                                                              MainAxisSize.max,
                                                                          mainAxisAlignment:
                                                                              MainAxisAlignment.end,
                                                                          children: [
                                                                            Flexible(
                                                                              child: Container(
                                                                                decoration: BoxDecoration(
                                                                                  color: Color(0x70FFFFFF),
                                                                                  boxShadow: [
                                                                                    BoxShadow(
                                                                                      blurRadius: 2.0,
                                                                                      color: Color(0x33FFFFFF),
                                                                                      offset: Offset(1.0, 1.0),
                                                                                    )
                                                                                  ],
                                                                                  borderRadius: BorderRadius.circular(18.0),
                                                                                  border: Border.all(
                                                                                    color: Color(0x494490DB),
                                                                                    width: 0.25,
                                                                                  ),
                                                                                ),
                                                                                child: Padding(
                                                                                  padding: EdgeInsetsDirectional.fromSTEB(15.0, 10.0, 15.0, 10.0),
                                                                                  child: Text(
                                                                                    valueOrDefault<String>(
                                                                                      FFAppState().promptText,
                                                                                      'Prompt Text',
                                                                                    ),
                                                                                    style: FlutterFlowTheme.of(context).bodyMedium.override(
                                                                                          fontFamily: 'Poppins',
                                                                                          color: FlutterFlowTheme.of(context).secondaryText,
                                                                                          fontSize: 11.5,
                                                                                          fontWeight: FontWeight.normal,
                                                                                        ),
                                                                                  ),
                                                                                ),
                                                                              ),
                                                                            ),
                                                                          ],
                                                                        ),
                                                                      ),
                                                                      Padding(
                                                                        padding: EdgeInsetsDirectional.fromSTEB(
                                                                            7.0,
                                                                            4.0,
                                                                            7.0,
                                                                            0.0),
                                                                        child:
                                                                            Container(
                                                                          width:
                                                                              30.0,
                                                                          height:
                                                                              30.0,
                                                                          decoration:
                                                                              BoxDecoration(
                                                                            color:
                                                                                FlutterFlowTheme.of(context).secondaryBackground,
                                                                            image:
                                                                                DecorationImage(
                                                                              fit: BoxFit.cover,
                                                                              image: Image.asset(
                                                                                'assets/images/image_1.png',
                                                                              ).image,
                                                                            ),
                                                                            shape:
                                                                                BoxShape.circle,
                                                                            border:
                                                                                Border.all(
                                                                              color: FlutterFlowTheme.of(context).customColor1,
                                                                              width: 1.5,
                                                                            ),
                                                                          ),
                                                                        ),
                                                                      ),
                                                                    ],
                                                                  ),
                                                                ),
                                                              ),
                                                              Padding(
                                                                padding: EdgeInsetsDirectional
                                                                    .fromSTEB(
                                                                        10.0,
                                                                        0.0,
                                                                        10.0,
                                                                        0.0),
                                                                child:
                                                                    Container(
                                                                  width: double
                                                                      .infinity,
                                                                  height: 50.0,
                                                                  constraints:
                                                                      BoxConstraints(
                                                                    maxWidth:
                                                                        700.0,
                                                                  ),
                                                                  decoration:
                                                                      BoxDecoration(),
                                                                  child: Row(
                                                                    mainAxisSize:
                                                                        MainAxisSize
                                                                            .max,
                                                                    children: [
                                                                      Padding(
                                                                        padding: EdgeInsetsDirectional.fromSTEB(
                                                                            0.0,
                                                                            3.0,
                                                                            0.0,
                                                                            0.0),
                                                                        child:
                                                                            Container(
                                                                          width:
                                                                              37.0,
                                                                          height:
                                                                              37.0,
                                                                          decoration:
                                                                              BoxDecoration(
                                                                            image:
                                                                                DecorationImage(
                                                                              fit: BoxFit.contain,
                                                                              image: Image.asset(
                                                                                'assets/images/bardStars.png',
                                                                              ).image,
                                                                            ),
                                                                          ),
                                                                        ),
                                                                      ),
                                                                      Lottie
                                                                          .asset(
                                                                        'assets/lottie_animations/6652-dote-typing-animation.json',
                                                                        width:
                                                                            38.0,
                                                                        height:
                                                                            72.0,
                                                                        fit: BoxFit
                                                                            .fitHeight,
                                                                        animate:
                                                                            true,
                                                                      ),
                                                                    ],
                                                                  ),
                                                                ),
                                                              ),
                                                            ],
                                                          ),
                                                        Padding(
                                                          padding:
                                                              EdgeInsetsDirectional
                                                                  .fromSTEB(
                                                                      0.0,
                                                                      30.0,
                                                                      0.0,
                                                                      30.0),
                                                          child: Container(
                                                            width:
                                                                double.infinity,
                                                            constraints:
                                                                BoxConstraints(
                                                              maxWidth: 750.0,
                                                            ),
                                                            decoration:
                                                                BoxDecoration(),
                                                            child: Padding(
                                                              padding:
                                                                  EdgeInsetsDirectional
                                                                      .fromSTEB(
                                                                          10.0,
                                                                          0.0,
                                                                          10.0,
                                                                          0.0),
                                                              child: Row(
                                                                mainAxisSize:
                                                                    MainAxisSize
                                                                        .max,
                                                                mainAxisAlignment:
                                                                    MainAxisAlignment
                                                                        .center,
                                                                children: [
                                                                  Expanded(
                                                                    child:
                                                                        Container(
                                                                      width: double
                                                                          .infinity,
                                                                      constraints:
                                                                          BoxConstraints(
                                                                        maxWidth:
                                                                            750.0,
                                                                      ),
                                                                      decoration:
                                                                          BoxDecoration(
                                                                        color: Color(
                                                                            0x69FFFFFF),
                                                                        borderRadius:
                                                                            BorderRadius.circular(30.0),
                                                                        border:
                                                                            Border.all(
                                                                          color:
                                                                              FlutterFlowTheme.of(context).secondaryText,
                                                                          width:
                                                                              0.25,
                                                                        ),
                                                                      ),
                                                                      child:
                                                                          Row(
                                                                        mainAxisSize:
                                                                            MainAxisSize.max,
                                                                        mainAxisAlignment:
                                                                            MainAxisAlignment.center,
                                                                        children: [
                                                                          Expanded(
                                                                            flex:
                                                                                3,
                                                                            child:
                                                                                Container(
                                                                              width: double.infinity,
                                                                              decoration: BoxDecoration(),
                                                                              child: Padding(
                                                                                padding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 8.0, 0.0),
                                                                                child: Container(
                                                                                  width: double.infinity,
                                                                                  child: TextFormField(
                                                                                    controller: _model.promptController,
                                                                                    onFieldSubmitted: (_) async {
                                                                                      var _shouldSetState = false;
                                                                                      FFAppState().update(() {
                                                                                        FFAppState().awaitingReply = true;
                                                                                        FFAppState().promptText = _model.promptController.text;
                                                                                      });
                                                                                      setState(() {
                                                                                        _model.promptController?.clear();
                                                                                      });
                                                                                      _model.chatContinue = await GoogleCLPChatGroup.generateResponseCall.call(
                                                                                        token: FFAppState().token,
                                                                                        prompt: FFAppState().promptText,
                                                                                        model: GoogleCLPChatGroup.getChatCall
                                                                                            .model(
                                                                                              chatGetChatResponse.jsonBody,
                                                                                            )
                                                                                            .toString(),
                                                                                        chatID: widget.chatRef,
                                                                                      );
                                                                                      _shouldSetState = true;
                                                                                      if ((_model.chatContinue?.succeeded ?? true)) {
                                                                                        FFAppState().update(() {
                                                                                          FFAppState().awaitingReply = false;
                                                                                        });
                                                                                        if (_shouldSetState) setState(() {});
                                                                                        return;
                                                                                      } else {
                                                                                        ScaffoldMessenger.of(context).showSnackBar(
                                                                                          SnackBar(
                                                                                            content: Text(
                                                                                              GoogleCLPChatGroup.generateResponseCall
                                                                                                  .apiMessage(
                                                                                                    (_model.chatContinue?.jsonBody ?? ''),
                                                                                                  )
                                                                                                  .toString(),
                                                                                              style: TextStyle(
                                                                                                color: FlutterFlowTheme.of(context).primaryText,
                                                                                              ),
                                                                                            ),
                                                                                            duration: Duration(milliseconds: 4000),
                                                                                            backgroundColor: FlutterFlowTheme.of(context).secondary,
                                                                                          ),
                                                                                        );
                                                                                        FFAppState().update(() {
                                                                                          FFAppState().awaitingReply = false;
                                                                                        });
                                                                                      }

                                                                                      if (_shouldSetState) setState(() {});
                                                                                    },
                                                                                    autofocus: true,
                                                                                    obscureText: false,
                                                                                    decoration: InputDecoration(
                                                                                      isDense: true,
                                                                                      labelStyle: FlutterFlowTheme.of(context).labelMedium.override(
                                                                                            fontFamily: 'Poppins',
                                                                                            fontSize: 12.0,
                                                                                          ),
                                                                                      hintText: 'Ask me anything...',
                                                                                      hintStyle: FlutterFlowTheme.of(context).labelMedium.override(
                                                                                            fontFamily: 'Poppins',
                                                                                            fontSize: 12.0,
                                                                                          ),
                                                                                      enabledBorder: InputBorder.none,
                                                                                      focusedBorder: InputBorder.none,
                                                                                      errorBorder: InputBorder.none,
                                                                                      focusedErrorBorder: InputBorder.none,
                                                                                      contentPadding: EdgeInsetsDirectional.fromSTEB(20.0, 15.0, 20.0, 15.0),
                                                                                    ),
                                                                                    style: FlutterFlowTheme.of(context).bodyMedium.override(
                                                                                          fontFamily: 'Poppins',
                                                                                          fontSize: 12.0,
                                                                                        ),
                                                                                    validator: _model.promptControllerValidator.asValidator(context),
                                                                                  ),
                                                                                ),
                                                                              ),
                                                                            ),
                                                                          ),
                                                                          SizedBox(
                                                                            height:
                                                                                40.0,
                                                                            child:
                                                                                VerticalDivider(
                                                                              thickness: 0.25,
                                                                              color: FlutterFlowTheme.of(context).secondaryText,
                                                                            ),
                                                                          ),
                                                                          Expanded(
                                                                            flex:
                                                                                1,
                                                                            child:
                                                                                Padding(
                                                                              padding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 20.0, 0.0),
                                                                              child: Container(
                                                                                width: 100.0,
                                                                                decoration: BoxDecoration(),
                                                                                child: Text(
                                                                                  valueOrDefault<String>(
                                                                                    GoogleCLPChatGroup.getChatCall
                                                                                        .model(
                                                                                          chatGetChatResponse.jsonBody,
                                                                                        )
                                                                                        .toString(),
                                                                                    'Model',
                                                                                  ),
                                                                                  textAlign: TextAlign.center,
                                                                                  style: FlutterFlowTheme.of(context).bodyMedium.override(
                                                                                        fontFamily: 'Poppins',
                                                                                        color: FlutterFlowTheme.of(context).secondaryText,
                                                                                        fontSize: 11.0,
                                                                                      ),
                                                                                ),
                                                                              ),
                                                                            ),
                                                                          ),
                                                                        ],
                                                                      ),
                                                                    ),
                                                                  ),
                                                                ],
                                                              ),
                                                            ),
                                                          ),
                                                        ),
                                                      ],
                                                    ),
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
