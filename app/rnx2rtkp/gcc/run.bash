
APP_PATH=/home/kauevestena/RTKLIB-mastert/app/rnx2rtkp/gcc/rnx2rtkp
OUT=/home/kauevestena/Dropbox/laix/lais/laix.pos

CONF=/home/kauevestena/RTKLIB-mastert/app/rnx2rtkp/gcc/opts.conf

RINEX=/home/kauevestena/arquivos/INVERNO/SAGA/RINEX/saga2051_60.14o
RINEXNAV=/home/kauevestena/arquivos/INVERNO/SAGA/RINEX/saga2051.14n
sp3_1=/home/kauevestena/arquivos/INVERNO/SAGA/arquivos/igs18024.sp3
clk=/home/kauevestena/arquivos/INVERNO/SAGA/arquivos/grg18024.clk

# echo $APP_PATH

echo $APP_PATH -k $CONF -o $OUT $RINEX $RINEXNAV $sp3_1 $clk

$APP_PATH -k $CONF -o $OUT $RINEX $RINEXNAV $sp3_1 $clk

