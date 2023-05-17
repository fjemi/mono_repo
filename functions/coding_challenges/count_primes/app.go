package main

import (
  "fmt"
)

func count_prime (n int) int {  
  // cases for n <= 2
  if n < 2 {
    return 0
  } else if n == 2 {
    return 1
  }
  
  // store primes
  primes := []int{2}
  
  for i := 3; i < n; i++ {
    var is_prime bool = true
    
    for j := 0; j < len(primes); j++ {
      // check if num is prime
      if i % primes[j] == 0 {
        is_prime = false
        break
      }
    }
    // add prime num to `prime` slice
    if is_prime {
      primes = append(primes, i)
    }
  }
  
  return len(primes)
}

func main () {
  var n int = 5
  fmt.Println(count_prime(n))
}
