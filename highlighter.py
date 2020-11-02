from PySide2 import QtCore
import re
from PySide2.QtCore import Qt
from PySide2.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor

class Highlighter(QSyntaxHighlighter):
    def highlightBlock(self, text):
        # TODO highlighter should give params different color?
        # Highlight keywords
        keywords = ["\\bcode\\b","\\bLPSTR\\b","\\bSIZE_T\\b","\\bLPVOID\\b","\\bDWORD\\b","\\bclock_t\\b","\\bthis\\b","\\bUINT\\b","\\bHANDLE\\b","\\blonglong\\b","\\bushort\\b","\\bFILE\\b","\\bulong\\b","\\bbyte\\b","\\bfalse\\b","\\btrue\\b","\\buint\\b","\\bsize_t\\b","\\bundefined\\d*\\b","\\bchar\\b", "\\bclass\\b", "\\bconst\\b", "\\bdouble\\b", "\\benum\\b", "\\bexplicit\\b","\\bfriend\\b", "\\binline\\b", "\\bint\\b","\\blong\\b", "\\bnamespace\\b", "\\boperator\\b","\\bprivate\\b", "\\bprotected\\b", "\\bpublic\\b","\\bshort\\b", "\\bsignals\\b", "\\bsigned\\b","\\bslots\\b", "\\bstatic\\b", "\\bstruct\\b","\\btemplate\\b", "\\btypedef\\b", "\\btypename\\b","\\bunion\\b", "\\bunsigned\\b", "\\bvirtual\\b","\\bvoid\\b", "\\bvolatile\\b", "\\bbool\\b"]
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor.fromRgb(62,156,202))
        for keyword in keywords:
            for match in re.finditer(keyword, text):
                self.setFormat(match.start(), match.end() - match.start(), keyword_format)
        # Highlight flow words
        flow_words = ["\\breturn\\b","\\bif\\b","\\belse\\b","\\bswitch\\b","\\bcase\\b","\\bwhile\\b","\\bfor\\b","\\bdo\\b","\\bgoto\\b"]
        flow_format = QTextCharFormat()
        flow_format.setForeground(QColor.fromRgb(197,134,192))
        for flow in flow_words:
            for match in re.finditer(flow, text):
                self.setFormat(match.start(), match.end() - match.start(), flow_format)
        # Highlight functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor.fromRgb(220,220,170))
        function_pattern = "\\b\\w+(?=\\()"
        for match in re.finditer(function_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), function_format)
        # Highlight comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor.fromRgb(82,153,85))
        comment_pattern = "\/\/.*$"
        for match in re.finditer(comment_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), comment_format)
        multi_comment_pattern = "(?s)\\/\\*.*?\\*\\/"
        for match in re.finditer(multi_comment_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), comment_format)
        # Highlight string constants
        const_format = QTextCharFormat()
        const_format.setForeground(QColor.fromRgb(206,145,120))
        string_consts = "\"(.*?)\""
        for match in re.finditer(string_consts, text):
            self.setFormat(match.start(), match.end() - match.start(), const_format)
        # Highlight numeric constants
        num_const_format = QTextCharFormat()
        num_const_format.setForeground(QColor.fromRgb(181,206,168))
        num_consts = "\\b\\d+\\b"
        for match in re.finditer(num_consts, text):
            self.setFormat(match.start(), match.end() - match.start(), num_const_format)
        hex_const = "0x[0-9a-f]+\\b"
        for match in re.finditer(hex_const, text):
            self.setFormat(match.start(), match.end() - match.start(), num_const_format)
        # Highlight data
        data_format = QTextCharFormat()
        data_format.setForeground(QColor.fromRgb(142,230,237))
        data_consts = "\\b_?DAT_[0-9a-zA-Z]+\\b"
        for match in re.finditer(data_consts, text):
            self.setFormat(match.start(), match.end() - match.start(), data_format)
        # Highlight CPP Class paths
        cpp_format = QTextCharFormat()
        cpp_format.setForeground(QColor.fromRgb(142,230,237))
        cpp_path = "\\b\\w*(?=::)"
        for match in re.finditer(cpp_path, text):
            self.setFormat(match.start(), match.end() - match.start(), cpp_format)

        
