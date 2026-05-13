#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

#define MAX_LEN 1000
#define MAX_TOKENS 100

// 十六进制转十进制
long hexToDec(const char *hex) {
    long res = 0;
    int i;
    char c;
    for (i = 0; i < (int)strlen(hex); i++) {
        c = tolower(hex[i]);
        res *= 16;
        if (isdigit(c))
            res += c - '0';
        else if (c >= 'a' && c <= 'f')
            res += 10 + (c - 'a');
    }
    return res;
}

int main() {
    // char指针数组
    const char *K[] = {
        "", // 0号
        "int", "void", "break", "float",
        "while", "do", "struct", "const",
        "case", "for", "return", "if",
        "default", "else"
    };
    const char *P[] = {
        "", // 0号
        "-", "/", "(", ")", "==", "<=",
        "<", "+", "*", ">", "=", ",",
        ";", "++", "{", "}"
    };
    
    char I[MAX_TOKENS][MAX_LEN];   // 标识符表
    char C1[MAX_TOKENS][MAX_LEN];  // 整数常量表
    char C2[MAX_TOKENS][MAX_LEN];  // 实数常量表
    char CT[MAX_TOKENS][MAX_LEN];  // 字符常量表
    char ST[MAX_TOKENS][MAX_LEN];  // 字符串常量表

    int I_size = 0, C1_size = 0, C2_size = 0, CT_size = 0, ST_size = 0;

    char s[MAX_LEN];
    char tokenOut[MAX_LEN * 4] = "Token :";
    int haveError = 0; // 0 表示 false, 1 表示 true
    int i = 0, j;

    // 读取一行输入
    fgets(s, MAX_LEN, stdin);
    int n = (int)strlen(s);
    // 去掉 fgets 可能读入的换行符或回车
    if (n > 0 && s[n - 1] == '\n') {
        s[n - 1] = '\0';
        n--;
    }
    if (n > 0 && s[n - 1] == '\r') {
        s[n - 1] = '\0';
        n--;
    }

    char word[MAX_LEN], num[MAX_LEN], ch[4], str[MAX_LEN];
    char op1[3], op2[3];
    char tempHex[MAX_LEN];
    int kid, id, pid, isHex, isFloat;

    while (i < n && !haveError) {
        // 关键字/标识符
        if (isalpha(s[i])) {
            int word_idx = 0;
            while (i < n && isalnum(s[i])) {
                word[word_idx++] = s[i];
                i++;
            }
            word[word_idx] = '\0';

            // 查关键字
            kid = -1;
            for (j = 1; j < 15; j++) {
                if (strcmp(K[j], word) == 0) {
                    kid = j;
                    break;
                }
            }

            if (kid != -1) {
                char temp[32];
                sprintf(temp, "(K %d)", kid);
                strcat(tokenOut, temp);
            } else {
                // 查/加入标识符表
                id = -1;
                for (j = 0; j < I_size; j++) {
                    if (strcmp(I[j], word) == 0) {
                        id = j + 1;
                        break;
                    }
                }
                if (id == -1) {
                    strcpy(I[I_size], word);
                    I_size++;
                    id = I_size;
                }
                char temp[32];
                sprintf(temp, "(I %d)", id);
                strcat(tokenOut, temp);
            }
        }
        // 数字
        else if (isdigit(s[i])) {
            int num_idx = 0;
            isHex = 0;
            isFloat = 0;
            num[0] = '\0';

            if (s[i] == '0' && i + 1 < n && tolower(s[i + 1]) == 'x') {
                isHex = 1;
                num[num_idx++] = s[i++];
                num[num_idx++] = s[i++];
                while (i < n && isxdigit(s[i])) {
                    num[num_idx++] = s[i];
                    i++;
                }
                num[num_idx] = '\0';
                
                // 提取 0x 后面的部分
                strcpy(tempHex, num + 2);
                long dec = hexToDec(tempHex);
                sprintf(num, "%ld", dec);
            } else {
                while (i < n && isdigit(s[i])) {
                    num[num_idx++] = s[i];
                    i++;
                }
                num[num_idx] = '\0';

                // 小数点
                if (i < n && s[i] == '.') {
                    isFloat = 1;
                    num[num_idx++] = s[i];
                    i++;
                    while (i < n && isdigit(s[i])) {
                        num[num_idx++] = s[i];
                        i++;
                    }
                    num[num_idx] = '\0';
                }

                // 科学计数法 e
                if (i < n && (s[i] == 'e' || s[i] == 'E')) {
                    isFloat = 1;
                    num[num_idx++] = s[i];
                    i++;

                    if (i < n && (s[i] == '+' || s[i] == '-')) {
                        num[num_idx++] = s[i];
                        i++;
                    }

                    while (i < n && isdigit(s[i])) {
                        num[num_idx++] = s[i];
                        i++;
                    }
                    num[num_idx] = '\0';
                }
            }

            char temp[32];
            if (isFloat) {
                id = -1;
                for (j = 0; j < C2_size; j++) {
                    if (strcmp(C2[j], num) == 0) {
                        id = j + 1;
                        break;
                    }
                }
                if (id == -1) {
                    strcpy(C2[C2_size], num);
                    C2_size++;
                    id = C2_size;
                }
                sprintf(temp, "(C2 %d)", id);
                strcat(tokenOut, temp);
            } else {
                id = -1;
                for (j = 0; j < C1_size; j++) {
                    if (strcmp(C1[j], num) == 0) {
                        id = j + 1;
                        break;
                    }
                }
                if (id == -1) {
                    strcpy(C1[C1_size], num);
                    C1_size++;
                    id = C1_size;
                }
                sprintf(temp, "(C1 %d)", id);
                strcat(tokenOut, temp);
            }
        }
        // 字符常量
        else if (s[i] == '\'') {
            i++;
            if (i >= n || i + 1 >= n || s[i + 1] != '\'') {
                haveError = 1;
                break;
            }
            ch[0] = s[i];
            ch[1] = '\0';
            i++;
            if (s[i] != '\'') {
                haveError = 1;
                break;
            }
            i++;

            id = -1;
            for (j = 0; j < CT_size; j++) {
                if (strcmp(CT[j], ch) == 0) {
                    id = j + 1;
                    break;
                }
            }
            if (id == -1) {
                strcpy(CT[CT_size], ch);
                CT_size++;
                id = CT_size;
            }
            char temp[32];
            sprintf(temp, "(CT %d)", id);
            strcat(tokenOut, temp);
        }
        // 字符串常量
        else if (s[i] == '"') {
            i++;
            int str_idx = 0;
            while (i < n && s[i] != '"') {
                str[str_idx++] = s[i];
                i++;
            }
            str[str_idx] = '\0';
            if (i >= n) {
                haveError = 1;
                break;
            }
            i++;

            id = -1;
            for (j = 0; j < ST_size; j++) {
                if (strcmp(ST[j], str) == 0) {
                    id = j + 1;
                    break;
                }
            }
            if (id == -1) {
                strcpy(ST[ST_size], str);
                ST_size++;
                id = ST_size;
            }
            char temp[32];
            sprintf(temp, "(ST %d)", id);
            strcat(tokenOut, temp);
        }
        // 界符
        else if (ispunct(s[i])) {
            op1[0] = s[i];
            op1[1] = '\0';
            if (i + 1 < n) {
                op2[0] = s[i];
                op2[1] = s[i + 1];
                op2[2] = '\0';
            } else {
                op2[0] = '\0';
            }

            pid = -1;
            // 先查两位
            for (j = 1; j < 17; j++) {
                if (strcmp(P[j], op2) == 0) {
                    pid = j;
                    break;
                }
            }
            if (pid != -1) {
                char temp[32];
                sprintf(temp, "(P %d)", pid);
                strcat(tokenOut, temp);
                i += 2;
                continue;
            }

            // 再查一位
            for (j = 1; j < 17; j++) {
                if (strcmp(P[j], op1) == 0) {
                    pid = j;
                    break;
                }
            }
            if (pid != -1) {
                char temp[32];
                sprintf(temp, "(P %d)", pid);
                strcat(tokenOut, temp);
                i++;
            } else {
                haveError = 1;
                break;
            }
        } else {
            haveError = 1;
            break;
        }
    }

    // 输出结果
    if (haveError) {
        printf("ERROR\n");
        return 0;
    }

    printf("%s\n", tokenOut);

    printf("I :");
    for (j = 0; j < I_size; j++) {
        if (j > 0) printf(" ");
        printf("%s", I[j]);
    }
    printf("\n");

    printf("C1 :");
    for (j = 0; j < C1_size; j++) {
        if (j > 0) printf(" ");
        printf("%s", C1[j]);
    }
    printf("\n");

    printf("C2 :");
    for (j = 0; j < C2_size; j++) {
        if (j > 0) printf(" ");
        printf("%s", C2[j]);
    }
    printf("\n");

    printf("CT :");
    for (j = 0; j < CT_size; j++) {
        if (j > 0) printf(" ");
        printf("%s", CT[j]);
    }
    printf("\n");

    printf("ST :");
    for (j = 0; j < ST_size; j++) {
        if (j > 0) printf(" ");
        printf("%s", ST[j]);
    }
    printf("\n");

    return 0;
}