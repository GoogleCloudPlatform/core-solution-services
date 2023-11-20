import '/components/dropdown_account/dropdown_account_widget.dart';
import '/flutter_flow/flutter_flow_icon_button.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import 'package:aligned_dialog/aligned_dialog.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'header_model.dart';
export 'header_model.dart';

class HeaderWidget extends StatefulWidget {
  const HeaderWidget({
    Key? key,
    required this.drawerCallback,
  }) : super(key: key);

  final Future<dynamic> Function()? drawerCallback;

  @override
  _HeaderWidgetState createState() => _HeaderWidgetState();
}

class _HeaderWidgetState extends State<HeaderWidget> {
  late HeaderModel _model;

  @override
  void setState(VoidCallback callback) {
    super.setState(callback);
    _model.onUpdate();
  }

  @override
  void initState() {
    super.initState();
    _model = createModel(context, () => HeaderModel());

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

    return Padding(
      padding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 0.0, 20.0),
      child: Row(
        mainAxisSize: MainAxisSize.max,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisSize: MainAxisSize.max,
            children: [
              Padding(
                padding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 10.0, 0.0),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8.0),
                  child: Image.asset(
                    'assets/images/bardStars.png',
                    width: 30.0,
                    height: 30.0,
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              Text(
                'Stretch',
                style: FlutterFlowTheme.of(context).titleLarge.override(
                      fontFamily: 'Product Sans',
                      fontSize: 20.0,
                      useGoogleFonts: false,
                    ),
              ),
              Padding(
                padding: EdgeInsetsDirectional.fromSTEB(0.0, 1.0, 0.0, 0.0),
                child: Text(
                  ' AI',
                  style: FlutterFlowTheme.of(context).titleLarge.override(
                        fontFamily: 'Product Sans',
                        color: FlutterFlowTheme.of(context).secondaryText,
                        fontSize: 20.0,
                        fontWeight: FontWeight.normal,
                        useGoogleFonts: false,
                      ),
                ),
              ),
            ],
          ),
          Container(
            width: 10.0,
            height: 10.0,
            decoration: BoxDecoration(),
          ),
          Row(
            mainAxisSize: MainAxisSize.max,
            children: [
              Builder(
                builder: (context) => FlutterFlowIconButton(
                  borderColor: Colors.transparent,
                  borderRadius: 6.0,
                  buttonSize: 40.0,
                  hoverColor: Color(0xBFFFFFFF),
                  hoverIconColor: FlutterFlowTheme.of(context).primaryText,
                  icon: Icon(
                    Icons.blur_on_rounded,
                    color: FlutterFlowTheme.of(context).primaryText,
                    size: 22.0,
                  ),
                  onPressed: () async {
                    await showAlignedDialog(
                      context: context,
                      isGlobal: false,
                      avoidOverflow: true,
                      targetAnchor: AlignmentDirectional(1.0, 1.0)
                          .resolve(Directionality.of(context)),
                      followerAnchor: AlignmentDirectional(0.0, 1.0)
                          .resolve(Directionality.of(context)),
                      builder: (dialogContext) {
                        return Material(
                          color: Colors.transparent,
                          child: DropdownAccountWidget(),
                        );
                      },
                    ).then((value) => setState(() {}));
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
