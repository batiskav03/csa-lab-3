# long gcd(long m, long n)
# {
#     while(m && n) if (m < n) n %= m; else m %= n;
#     return (m == 0L) ? n : m;
# }

# long lcm(long m, long n)
# {
#     return (m/gcd(m,n))*n;
# }


# int main(int argc, const char * argv[])
# {
#     long Res = 1;
#     for(int i = 2; i <= 20; ++i)
#     {
#         Res = lcm(Res,i);
#     }
#     cout << Res << endl;
# }


def gcd(m:int , n:int) -> int:
    while (m and n):
        if (m < n):
            n = n % m
        else:
            m = m % n
    result = n if (m == 0) else m
    if result > 2147483647:
        print("xyu")
    return result

def lcm(m: int, n: int) -> int:
    result: int = ((m//gcd(m,n)) * n)
    if result > 2147483647:
        print("xyu")
    return result

def main() -> int:
    res: int = 1;
    for i in range (2, 20):
        res = lcm(res, i)
    return res
print(main())



def foo():
    res = 1;
    tmp_res = 0
    i = 2
    while (i <= 20):
        m = res
        n = i
        while (m and n):
            if (m < n):
                n = n % m
            else:
                m = m % n
        if (m == 0):
            tmp_res = n
        if (m != 0):
            tmp_res = m
        m = res
        n = i
        tmp_res = (m / tmp_res) * i
        
        res = tmp_res
        i += 1
    print(res)
        
foo()


int res = 1;
int tmpres = 0;
int i = 2;
int m = 0;
int n = 0;
int cond = 1;
while (i <= 20) {
    m = res;
    n = i;
    cond = m and n;
    while (cond != 0) {
        if (m < n) {
            n = n % m;
        } else {
            m = m % n;
        }
    }
    if (m == 0) {
        tmpres = n;
    } else {
        tmpres = m;
    }
    tmpres = m / tmpres;
    tmpres = tmpres * i;
    res = tmpres;
    i = i + 1;
}

print (res)
        
# int main(int argc, const char * argv[])
# {
#     int Res = 1;
#     int tmp_res = 0;
#     for(int i = 2; i <= 20; ++i)
#     {
#         int m = Res;
#         int n = i;
#         while(m && n) {
#             if (m < n) n %= m;
#             if (m >= n) m %= n;
#         } 
#         if (m == 0) {
#             tmp_res = n;
#         } 
#         if (m != 0){
#             tmp_res = m;
#         }
#         m = Res;
#         n = i;
#         tmp_res = (m / tmp_res) * i;
        
#         Res = tmp_res;
#     }

# }