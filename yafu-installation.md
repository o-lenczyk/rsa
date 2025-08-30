1. git clone git@github.com:bbuhrow/yafu.git
2. install icc compiler (12GB)
3. make yafu USE_AVX512=1 USE_AVX2=1 USE_BMI2=1 ICELAKE=1 COMPILER=icx  
4. ./yafu "factor(123456789123456789)"
5. cp yafu /home/orest/.local/bin/  