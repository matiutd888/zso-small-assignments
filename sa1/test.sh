make
./run_formatter >fmt.out
if [ "$(diff fmt.out expected.out)" != "" ] 
then
    echo "Program error"
    rm -rf fmt.out
    exit 1 
fi
echo "All ok"
rm -rf fmt.out

