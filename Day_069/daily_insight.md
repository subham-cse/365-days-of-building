# Day 069: ARC Retain Cycles and Escaping Closures in Swift

**Language / Domain**: Swift

**The Core Concept / "Did You Know?"**:
Swift uses Automatic Reference Counting (ARC) to manage memory allocation. While ARC automates reference counting, it cannot automatically break strong reference cycles (where two object instances hold strong references to each other, preventing their reference counts from ever reaching zero).

A common memory leak trap occurs when using closures inside Swift classes. Closures in Swift are reference types that capture variables from their surrounding scope by reference. If a class instance stores an escaping closure as a property, and that closure captures `self` strongly within its body, a hidden retain cycle is established. The class instance will never be deallocated from RAM, leaking memory indefinitely.

**The Code Snippet**:
```swift
import Foundation

class NetworkDataFetcher {
    let url: URL
    var onComplete: ((Data?) -> Void)?
    var cachedData: Data?

    init(url: URL) {
        self.url = url
        print("NetworkDataFetcher initialized: \(url)")
    }

    // TRAP: Retain cycle created by capturing self strongly
    func setupUnsafeCallback() {
        self.onComplete = { data in
            // Strong reference to 'self' inside stored closure
            self.cachedData = data 
            print("Fetched data for \(self.url)")
        }
    }

    // SAFE PATTERN: Weak/Unowned capture list
    func setupSafeCallback() {
        self.onComplete = { [weak self] data in
            // Safely unwrap weak self reference
            guard let self = self else { return }
            self.cachedData = data
            print("Safely fetched data for \(self.url)")
        }
    }

    deinit {
        print("NetworkDataFetcher DEALLOCATED: \(url)")
    }
}

// Demonstrating memory leak vs safe cleanup
func runMemoryTest() {
    print("--- 1. Testing Unsafe Retain Cycle ---")
    var fetcher1: NetworkDataFetcher? = NetworkDataFetcher(url: URL(string: "https://api.example.com/v1")!)
    fetcher1?.setupUnsafeCallback()
    fetcher1 = nil // Object is NOT deallocated! Deinit is never called!

    print("\n--- 2. Testing Safe Memory Cleanup ---")
    var fetcher2: NetworkDataFetcher? = NetworkDataFetcher(url: URL(string: "https://api.example.com/v2")!)
    fetcher2?.setupSafeCallback()
    fetcher2 = nil // Deinit IS called successfully!
}

runMemoryTest()
```

**Under the Hood / Why It Happens**:
Every Swift class instance contains an internal retain count header. 
When `fetcher1` stores `onComplete`, `fetcher1` increases the closure's reference count by 1. Inside `setupUnsafeCallback`, the closure body captures `self` (`fetcher1`), which increments `fetcher1`'s ARC retain count from 1 to 2.

When `fetcher1 = nil` executes in caller scope, its reference count decrements from 2 to 1. Because the closure still holds a retain count of 1 on `fetcher1`, and `fetcher1` holds a reference to the closure, neither can be deallocated. `deinit` is never invoked, leading to a permanent memory leak.

Using `[weak self]` instructs the compiler to capture `self` as an optional reference without incrementing its ARC count. If `fetcher2` drops to zero retain count, Swift zeroes the weak pointer and frees heap allocation immediately.

**Key Takeaway / Safe Pattern**:
Always inspect closures stored as properties or passed to long-lived escaping handlers (like network tasks or event listeners). Use explicit capture lists (`[weak self]` or `[unowned self]`) whenever referencing `self` properties or methods inside stored closures.
