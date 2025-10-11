package main

import (
	"fmt"
	"github.com/klauspost/reedsolomon"
)

func main() {
	dataShards, parityShards := 4, 2
	rs, err := reedsolomon.New(dataShards, parityShards)
	if err != nil { panic(err) }

	// Each "shard" is the same length; data shards hold data, parity shards will be computed.
	shardSize := 1024
	shards := make([][]byte, dataShards+parityShards)
	for i := 0; i < dataShards; i++ {
		shards[i] = make([]byte, shardSize)
		for j := range shards[i] { shards[i][j] = byte(i) } // toy data
	}
	for i := dataShards; i < dataShards+parityShards; i++ {
		shards[i] = make([]byte, shardSize) // parity buffers
	}

	// Encode parity shards
	if err := rs.Encode(shards); err != nil { panic(err) }

	// Simulate losses (erasures): any 'nil' shard (or missing) can be reconstructed
	shards[1] = nil // lost data shard
	shards[4] = nil // lost parity shard

	ok, _ := rs.Verify(shards)
	fmt.Println("Verify before reconstruct:", ok) // usually false

	// Reconstruct the missing shards
	if err := rs.Reconstruct(shards); err != nil { panic(err) }

	ok, _ = rs.Verify(shards)
	fmt.Println("Verify after reconstruct:", ok) // true
}
