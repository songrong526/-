#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_TOKEN 100
#define MAX_LEX 32

// ---------------------
// Token 类型
// ---------------------
typedef enum {
    TOKEN_NONE,
    TOKEN_PROGRAM, TOKEN_VAR, TOKEN_INTEGER, TOKEN_REAL, TOKEN_CHAR,
    TOKEN_BEGIN, TOKEN_END, TOKEN_SEMICOLON, TOKEN_COLON, TOKEN_COMMA,
    TOKEN_ASSIGN, TOKEN_ID, TOKEN_NUMBER, TOKEN_EOF
} TokenType;

typedef struct {
    TokenType type;
    int value;              // 对应符号表或常数表索引，关键字可忽略
    char lexeme[MAX_LEX];   // 可选，用于调试
} Token;

// ---------------------
// 全局变量
// ---------------------
Token tokens[MAX_TOKEN];   // Token序列
int tokenCount = 0;        // Token数量
int currentPos = 0;        // 当前解析位置
Token currentToken;

// ---------------------
// 辅助函数
// ---------------------
void nextToken() {
    if (currentPos < tokenCount) {
        currentToken = tokens[currentPos++];
    } else {
        currentToken.type = TOKEN_EOF;
    }
}

void match(TokenType t) {
    if (currentToken.type == t) {
        nextToken();
    } else {
        printf("Syntax Error! Unexpected token: %s\n", currentToken.lexeme);
        exit(1);
    }
}

// ---------------------
// 递归下降语法分析器
// ---------------------
void PROGRAM();
void SUB_PROGRAM();
void VARIABLE();
void ID_SEQUENCE();
void TYPE();
void COM_SENTENCE();
void SEN_SEQUENCE();
void EVA_SENTENCE();
void EXPRESSION();
void TERM();
void FACTOR();

void PROGRAM() {
    match(TOKEN_PROGRAM);
    match(TOKEN_ID);
    SUB_PROGRAM();
    match(TOKEN_EOF);  // 序列结束
}

void SUB_PROGRAM() {
    VARIABLE();
    COM_SENTENCE();
}

void VARIABLE() {
    if (currentToken.type == TOKEN_VAR) {
        match(TOKEN_VAR);
        ID_SEQUENCE();
        match(TOKEN_COLON);
        TYPE();
        match(TOKEN_SEMICOLON);
    }
}

void ID_SEQUENCE() {
    match(TOKEN_ID);
    while (currentToken.type == TOKEN_COMMA) {
        match(TOKEN_COMMA);
        match(TOKEN_ID);
    }
}

void TYPE() {
    switch (currentToken.type) {
        case TOKEN_INTEGER: match(TOKEN_INTEGER); break;
        case TOKEN_REAL: match(TOKEN_REAL); break;
        case TOKEN_CHAR: match(TOKEN_CHAR); break;
        default:
            printf("Type Error! Unexpected token: %s\n", currentToken.lexeme);
            exit(1);
    }
}

void COM_SENTENCE() {
    match(TOKEN_BEGIN);
    SEN_SEQUENCE();
    match(TOKEN_END);
}

void SEN_SEQUENCE() {
    EVA_SENTENCE();
    while (currentToken.type == TOKEN_SEMICOLON) {
        match(TOKEN_SEMICOLON);
        EVA_SENTENCE();
    }
}

void EVA_SENTENCE() {
    match(TOKEN_ID);
    match(TOKEN_ASSIGN);
    EXPRESSION();
}

void EXPRESSION() {
    TERM();
    // 可扩展 + - 表达式
}

void TERM() {
    FACTOR();
    // 可扩展 * / 表达式
}

void FACTOR() {
    if (currentToken.type == TOKEN_ID) match(TOKEN_ID);
    else if (currentToken.type == TOKEN_NUMBER) match(TOKEN_NUMBER);
    else {
        printf("Factor Error! Unexpected token: %s\n", currentToken.lexeme);
        exit(1);
    }
}

// ---------------------
// 主程序示例
// ---------------------
int main() {
    // 这里手动填写一个 Token 序列作为示例（来自词法分析器）
    // program example var a,b: integer; begin a := 2; b := 3; end
    tokenCount = 13;
    tokens[0] = (Token){TOKEN_PROGRAM, -1, "program"};
    tokens[1] = (Token){TOKEN_ID, 1, "example"};
    tokens[2] = (Token){TOKEN_VAR, -1, "var"};
    tokens[3] = (Token){TOKEN_ID, 2, "a"};
    tokens[4] = (Token){TOKEN_COMMA, -1, ","};
    tokens[5] = (Token){TOKEN_ID, 3, "b"};
    tokens[6] = (Token){TOKEN_COLON, -1, ":"};
    tokens[7] = (Token){TOKEN_INTEGER, -1, "integer"};
    tokens[8] = (Token){TOKEN_SEMICOLON, -1, ";"};
    tokens[9] = (Token){TOKEN_BEGIN, -1, "begin"};
    tokens[10] = (Token){TOKEN_ID, 2, "a"};
    tokens[11] = (Token){TOKEN_ASSIGN, -1, ":="};
    tokens[12] = (Token){TOKEN_NUMBER, 2, "2"};
    // 可以继续扩展 b := 3; end 等

    currentPos = 0;
    nextToken();

    PROGRAM();

    printf("Parsing finished successfully!\n");

    return 0;
}