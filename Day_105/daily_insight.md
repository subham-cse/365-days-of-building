# Day 105: String Pool Caching and Primitive Wrapper Boxing Pitfalls
- **Language / Domain**: Java
- **The Core Concept / "Did You Know?"**: Java optimizes memory using pools for both `String` literals (the String Pool) and small primitive wrapper objects (`IntegerCache` for values between `-128` and `127`). 

Because of this caching mechanism, using loose equality `==` on object references can yield deceptively inconsistent results: `Integer a = 100; Integer b = 100; a == b` evaluates to `true`, but `Integer c = 200; Integer d = 200; c == d` evaluates to `false`!

- **The Code Snippet**:
```java
public class JavaCachingPitfalls {
    public static void main(String[] args) {
        // Integer Caching Trap (-128 to 127)
        Integer x1 = 100;
        Integer x2 = 100;
        System.out.println("100 == 100: " + (x1 == x2)); // true (cached object)

        Integer y1 = 200;
        Integer y2 = 200;
        System.out.println("200 == 200: " + (y1 == y2)); // false (different heap instances!)

        System.out.println("200 .equals 200: " + y1.equals(y2)); // true (safe value comparison)

        // String Pool Trap
        String s1 = "Hello";
        String s2 = "Hello";
        String s3 = new String("Hello");

        System.out.println("Literal == Literal: " + (s1 == s2)); // true (points to same pool entry)
        System.out.println("Literal == New String: " + (s1 == s3)); // false (heap vs pool)
        System.out.println("s1.equals(s3): " + s1.equals(s3)); // true
    }
}
```

- **Under the Hood / Why It Happens**:
During classloading, Java caches boxed primitives in `java.lang.Integer.IntegerCache` for values `[-128, 127]`. Auto-boxing (`Integer.valueOf(int)`) returns cached references for values in range. For numbers outside that range, `valueOf` creates a new instance on the heap using `new Integer(i)`.

Similarly, String literals are stored in the JVM's native `StringTable` string pool (implemented as a hashtable in C++ memory). `new String("Hello")` bypasses pool reuse, creating a new heap object that references the underlying `byte[]` array.

- **Key Takeaway / Safe Pattern**:
Never use reference equality (`==`) to compare objects or wrapper types in Java! Always use `.equals()` for value equality across `String`, `Integer`, `Long`, and all object types.
