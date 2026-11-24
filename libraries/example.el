// ============================================================
//  example.el — EzLibrary Example
//
//  Demonstrates the .el command-definition format.
//
//  Usage in .ez scripts:
//    import example.el
//    Greet("World")
//    Add(5, 3)
// ============================================================

Def {
  Library.name: "Example"
  Library.version: v1.0
  Package.identifier: "ezcode.demo.example"
}

Cmd {
  Syntax: 'Greet("{name}")'
  Func: 'print("Hello, " + name + "!")'
}

Cmd {
  Syntax: 'Add({a}, {b})'
  Func: 'result = int(a) + int(b); print(str(a) + " + " + str(b) + " = " + str(result))'
}
