```head -c 2M /dev/urandom > base.bin```
```cp base.bin modified.bin```

```dd if=/dev/urandom of=modified.bin bs=1 seek=262144 count=4096 conv=notrunc status=none```
```
for off in 262144 983040 1572864; do 
  dd if=/dev/urandom of=modified.bin bs=1 seek=$off count=2048 conv=notrunc status=none
done
```

```python simhash_complete.py base.bin modified.bin --ngram 5 --bitlen 128```
```python simhash_complete_chunked.py base.bin modified.bin --ngram 5 --bitlen 128 --block-size 64K```