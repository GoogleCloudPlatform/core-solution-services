import 'package:dropdown_button2/dropdown_button2.dart';

import 'form_field_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

class FlutterFlowDropDown<T> extends StatefulWidget {
  const FlutterFlowDropDown({
    required this.controller,
    this.hintText,
    this.searchHintText,
    required this.options,
    this.optionLabels,
    required this.onChanged,
    this.icon,
    this.width,
    this.height,
    this.fillColor,
    this.searchHintTextStyle,
    this.searchCursorColor,
    required this.textStyle,
    required this.elevation,
    required this.borderWidth,
    required this.borderRadius,
    required this.borderColor,
    required this.margin,
    this.hidesUnderline = false,
    this.disabled = false,
    this.isSearchable = false,
  });

  final FormFieldController<T> controller;
  final String? hintText;
  final String? searchHintText;
  final List<T> options;
  final List<String>? optionLabels;
  final Function(T?) onChanged;
  final Widget? icon;
  final double? width;
  final double? height;
  final Color? fillColor;
  final TextStyle? searchHintTextStyle;
  final Color? searchCursorColor;
  final TextStyle textStyle;
  final double elevation;
  final double borderWidth;
  final double borderRadius;
  final Color borderColor;
  final EdgeInsetsGeometry margin;
  final bool hidesUnderline;
  final bool disabled;
  final bool isSearchable;

  @override
  State<FlutterFlowDropDown<T>> createState() => _FlutterFlowDropDownState<T>();
}

class _FlutterFlowDropDownState<T> extends State<FlutterFlowDropDown<T>> {
  final TextEditingController _textEditingController = TextEditingController();

  void Function() get listener =>
      () => widget.onChanged(widget.controller.value);

  @override
  void initState() {
    widget.controller.addListener(listener);
    super.initState();
  }

  @override
  void dispose() {
    widget.controller.removeListener(listener);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final value = widget.options.contains(widget.controller.value)
        ? widget.controller.value
        : null;
    final items = widget.options
        .asMap()
        .entries
        .map(
          (option) => DropdownMenuItem<T>(
            value: option.value,
            child: Text(
              widget.optionLabels == null ||
                      widget.optionLabels!.length < option.key + 1
                  ? option.value.toString()
                  : widget.optionLabels![option.key],
              style: widget.textStyle,
            ),
          ),
        )
        .toList();
    final hintText = widget.hintText != null
        ? Text(widget.hintText!, style: widget.textStyle)
        : null;
    void Function(T?)? onChanged =
        !widget.disabled ? (value) => widget.controller.value = value : null;
    final dropdownWidget = widget.isSearchable
        ? _buildSearchableDropdown(value, items, onChanged, hintText)
        : _buildNonSearchableDropdown(value, items, onChanged, hintText);
    final childWidget = DecoratedBox(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(widget.borderRadius),
        border: Border.all(
          color: widget.borderColor,
          width: widget.borderWidth,
        ),
        color: widget.fillColor,
      ),
      child: Padding(
        padding: widget.margin,
        child: widget.hidesUnderline
            ? DropdownButtonHideUnderline(child: dropdownWidget)
            : dropdownWidget,
      ),
    );
    if (widget.height != null || widget.width != null) {
      return Container(
        width: widget.width,
        height: widget.height,
        child: childWidget,
      );
    }
    return childWidget;
  }

  Widget _buildNonSearchableDropdown(
    T? value,
    List<DropdownMenuItem<T>>? items,
    void Function(T?)? onChanged,
    Text? hintText,
  ) {
    return DropdownButton<T>(
      value: value,
      hint: hintText,
      items: items,
      elevation: widget.elevation.toInt(),
      onChanged: onChanged,
      icon: widget.icon,
      isExpanded: true,
      dropdownColor: widget.fillColor,
      focusColor: Colors.transparent,
    );
  }

  Widget _buildSearchableDropdown(
    T? value,
    List<DropdownMenuItem<T>>? items,
    void Function(T?)? onChanged,
    Text? hintText,
  ) {
    final overlayColor = MaterialStateProperty.resolveWith<Color?>((states) =>
        states.contains(MaterialState.focused) ? Colors.transparent : null);
    final iconStyleData = widget.icon != null
        ? IconStyleData(icon: widget.icon!)
        : const IconStyleData();
    return DropdownButton2<T>(
      value: value,
      hint: hintText,
      items: items,
      iconStyleData: iconStyleData,
      buttonStyleData: ButtonStyleData(
        elevation: widget.elevation.toInt(),
        overlayColor: overlayColor,
      ),
      menuItemStyleData: MenuItemStyleData(overlayColor: overlayColor),
      dropdownStyleData: DropdownStyleData(
        elevation: widget.elevation.toInt(),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(4),
          color: widget.fillColor,
        ),
      ),
      onChanged: onChanged,
      isExpanded: true,
      dropdownSearchData: DropdownSearchData<T>(
        searchController: _textEditingController,
        searchInnerWidgetHeight: 50,
        searchInnerWidget: Container(
          height: 50,
          padding: const EdgeInsets.only(
            top: 8,
            bottom: 4,
            right: 8,
            left: 8,
          ),
          child: TextFormField(
            expands: true,
            maxLines: null,
            controller: _textEditingController,
            cursorColor: widget.searchCursorColor,
            decoration: InputDecoration(
              isDense: true,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 10,
                vertical: 8,
              ),
              hintText: widget.searchHintText,
              hintStyle: widget.searchHintTextStyle,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
        searchMatchFn: (item, searchValue) {
          return item.value
              .toString()
              .toLowerCase()
              .contains(searchValue.toLowerCase());
        },
      ),

      //This to clear the search value when you close the menu
      onMenuStateChange: (isOpen) {
        if (!isOpen) {
          _textEditingController.clear();
        }
      },
    );
  }
}
