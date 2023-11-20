import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'logo_header_model.dart';
export 'logo_header_model.dart';

class LogoHeaderWidget extends StatefulWidget {
  const LogoHeaderWidget({Key? key}) : super(key: key);

  @override
  _LogoHeaderWidgetState createState() => _LogoHeaderWidgetState();
}

class _LogoHeaderWidgetState extends State<LogoHeaderWidget> {
  late LogoHeaderModel _model;

  @override
  void setState(VoidCallback callback) {
    super.setState(callback);
    _model.onUpdate();
  }

  @override
  void initState() {
    super.initState();
    _model = createModel(context, () => LogoHeaderModel());

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

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Padding(
          padding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 16.0, 5.0),
          child: ClipRRect(
            // borderRadius: BorderRadius.circular(8.0),
            child: Image.asset(
              'assets/images/app-logo.png',
              width: 180.0,
              height: 150.0,
              // fit: BoxFit.cover,
            ),
          ),
        ),
        Row(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'GenAI ',
              style: FlutterFlowTheme.of(context).bodyMedium.override(
                    fontFamily: 'Poppins',
                    fontSize: 22.0,
                    fontWeight: FontWeight.w500,
                  ),
            ),
            Padding(
              padding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 15.0, 0.0),
              child: Text(
                'for Enterprise',
                style: FlutterFlowTheme.of(context).bodyMedium.override(
                      fontFamily: 'Poppins',
                      color: FlutterFlowTheme.of(context).secondaryText,
                      fontSize: 22.0,
                    ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}
