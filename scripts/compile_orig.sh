# running:
# sh scripts/compile_orig.sh

cd /home/RTKLIB/rtklib_orig/RTKLIB/app/rnx2rtkp/gcc

# make CFLAGS="-std=c99"
make 


# compile crx2rnx:
cd /home/RTKLIB/app/rnx2rtkp/gcc

# make clean CFLAGS="-std=c99"
make CFLAGS="-std=c99"