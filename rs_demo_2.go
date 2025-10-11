package main

import (
	"fmt"
	"github.com/klauspost/reedsolomon"
)

// Splits the message into k shards.
// It returns the shards and the size of each shard.
func split(msg []byte, k int) ([][]byte, int) {
	shardSize := (len(msg) + k - 1) / k 
	shards := make([][]byte, k)
	for i := 0; i < k; i++ {
		shards[i] = make([]byte, shardSize)
		start := i * shardSize
		end := start + shardSize
		if start >= len(msg) {
			continue
		}
		if end > len(msg) {
			end = len(msg)
		}
		copy(shards[i], msg[start:end])
	}
	return shards, shardSize
}

// join concatena i primi k shard e tronca alla lunghezza originale.
func join(shards [][]byte, k int, origLen int) []byte {
	out := make([]byte, 0, k*len(shards[0]))
	for i := 0; i < k; i++ {
		out = append(out, shards[i]...)
	}
	return out[:origLen]
}

func main() {
	msg := []byte("HELLO_RS") // original message
	k, m := 4, 2              // dataShards, parityShards

	// 1) Split the message into k data shards
	dataShards, shardSize := split(msg, k)

	// 2) Allocate parity shards
	shards := make([][]byte, k+m)
	copy(shards, dataShards)
	for i := k; i < k+m; i++ {
		shards[i] = make([]byte, shardSize)
	}

	// 3) Create Reed-Solomon encoder and encode
	rs, err := reedsolomon.New(k, m)
	if err != nil {
		panic(err)
	}
	if err := rs.Encode(shards); err != nil {
		panic(err)
	}

	fmt.Println("Data shards before erasures:")
	for i := 0; i < k; i++ {
		fmt.Printf("data shard %d: %q\n", i, string(shards[i]))
	}
	fmt.Println("Calculated parity shards:")
	for i := k; i < k+m; i++ {
		fmt.Printf("parity shard %d: (hex: % X)\n", i-k, shards[i])
	}

	// 4) Simulate the loss of some shards
	shards[1] = nil // we lose a data shard
	shards[4] = nil // we lose a parity shard

	// 5) Print shards after erasures
	fmt.Println("\nShards after erasures:")
	for i := 0; i < k+m; i++ {
		if shards[i] == nil {
			fmt.Printf("shard %d: missing\n", i)
		} else {
			fmt.Printf("shard %d: %q\n", i, string(shards[i]))
		}
	}

	// 6) Reconstruct the missing shards (up to m)
	if err := rs.Reconstruct(shards); err != nil {
		panic(err)
	}

	// 7) Reassemble the original message
	recovered := join(shards, k, len(msg))
	fmt.Println("\nReconstructed message:", string(recovered))
}
