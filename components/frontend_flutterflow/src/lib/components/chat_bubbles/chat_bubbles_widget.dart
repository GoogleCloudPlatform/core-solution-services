import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'chat_bubbles_model.dart';
export 'chat_bubbles_model.dart';

class ChatBubblesWidget extends StatefulWidget {
  const ChatBubblesWidget({
    Key? key,
    required this.humanMessage,
    required this.aiMessage,
    required this.human,
    required this.ai,
  }) : super(key: key);

  final String? humanMessage;
  final String? aiMessage;
  final bool? human;
  final bool? ai;

  @override
  _ChatBubblesWidgetState createState() => _ChatBubblesWidgetState();
}

class _ChatBubblesWidgetState extends State<ChatBubblesWidget> {
  late ChatBubblesModel _model;

  @override
  void setState(VoidCallback callback) {
    super.setState(callback);
    _model.onUpdate();
  }

  @override
  void initState() {
    super.initState();
    _model = createModel(context, () => ChatBubblesModel());

    WidgetsBinding.instance.addPostFrameCallback((_) => setState(() {}));
  }

  @override
  void dispose() {
    _model.maybeDispose();

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    context.watch<FFAppState>();

    return Container(
      decoration: BoxDecoration(),
      child: Column(
        mainAxisSize: MainAxisSize.max,
        children: [
          if (widget.ai == true)
            Padding(
              padding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 0.0, 20.0),
              child: Row(
                mainAxisSize: MainAxisSize.max,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: EdgeInsetsDirectional.fromSTEB(0.0, 3.0, 0.0, 0.0),
                    child: Container(
                      width: 37.0,
                      height: 37.0,
                      decoration: BoxDecoration(
                        image: DecorationImage(
                          fit: BoxFit.contain,
                          image: Image.asset(
                            'assets/images/Mask_group.png',
                          ).image,
                        ),
                      ),
                    ),
                  ),
                  Expanded(
                    flex: 4,
                    child: Row(
                      mainAxisSize: MainAxisSize.max,
                      children: [
                        Flexible(
                          child: Container(
                            decoration: BoxDecoration(
                              color: Color(0x9890B6F2),
                              boxShadow: [
                                BoxShadow(
                                  blurRadius: 2.0,
                                  color: Color(0x33FFFFFF),
                                  offset: Offset(1.0, 1.0),
                                )
                              ],
                              borderRadius: BorderRadius.circular(18.0),
                              border: Border.all(
                                color: Color(0x49FFFFFF),
                                width: 0.25,
                              ),
                            ),
                            child: Padding(
                              padding: EdgeInsetsDirectional.fromSTEB(
                                  15.0, 10.0, 15.0, 10.0),
                              child: Text(
                                widget.aiMessage!,
                                style: FlutterFlowTheme.of(context)
                                    .bodyMedium
                                    .override(
                                      fontFamily: 'Poppins',
                                      color: FlutterFlowTheme.of(context)
                                          .primaryText,
                                      fontSize: 11.5,
                                      fontWeight: FontWeight.w500,
                                    ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    flex: 1,
                    child: Container(
                      width: 100.0,
                      height: 20.0,
                      decoration: BoxDecoration(),
                    ),
                  ),
                ],
              ),
            ),
          if (widget.human == true)
            Padding(
              padding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 0.0, 20.0),
              child: Row(
                mainAxisSize: MainAxisSize.max,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    flex: 1,
                    child: Container(
                      width: 100.0,
                      height: 20.0,
                      decoration: BoxDecoration(),
                    ),
                  ),
                  Expanded(
                    flex: 4,
                    child: Row(
                      mainAxisSize: MainAxisSize.max,
                      mainAxisAlignment: MainAxisAlignment.end,
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
                              padding: EdgeInsetsDirectional.fromSTEB(
                                  15.0, 10.0, 15.0, 10.0),
                              child: Text(
                                widget.humanMessage!,
                                style: FlutterFlowTheme.of(context)
                                    .bodyMedium
                                    .override(
                                      fontFamily: 'Poppins',
                                      color: FlutterFlowTheme.of(context)
                                          .secondaryText,
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
                    padding: EdgeInsetsDirectional.fromSTEB(7.0, 4.0, 7.0, 0.0),
                    child: Container(
                      width: 30.0,
                      height: 30.0,
                      decoration: BoxDecoration(
                        color: FlutterFlowTheme.of(context).secondaryBackground,
                        image: DecorationImage(
                          fit: BoxFit.cover,
                          image: Image.asset(
                            'assets/images/image_1.png',
                          ).image,
                        ),
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: FlutterFlowTheme.of(context).customColor1,
                          width: 1.5,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
