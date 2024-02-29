int a = 1;
int b = 1;
int sum = 0;
int c =0;
int cond = 0;
while (b<4000000) {
    cond = b % 2;
    if (cond==0) {
       sum = sum + b;
    }
    c = a + b;
    a = b;
    b = c;
}