import 'dart:convert';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:timeago/timeago.dart' as timeago;
import 'lat_lng.dart';
import 'place.dart';
import 'uploaded_file.dart';

List<dynamic>? reverseOrder(List<dynamic>? messages) {
  // reverse order of json list
  if (messages != null) {
    return messages.reversed.toList();
  } else {
    return null;
  }
}

String? dateTimeFormat(dynamic datetime) {
  // format json datetime into relative date format, e.g. 5 minutes ago
  if (datetime != null) {
    DateTime dateTime = DateTime.parse(datetime);
    return timeago.format(dateTime);
  } else {
    return null;
  }
}
