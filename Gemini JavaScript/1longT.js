/***************************************************************************************************
 * FULL, DETAILED, IN-DEPTH JAVASCRIPT TUTORIAL — SINGLE GIANT FILE (Option A)
 *
 * Run this with Node.js (>=14) for most examples. Some DOM examples are annotated and won't run in Node.
 * This file mixes runnable code and heavily-commented explanations. Read top-to-bottom; each section
 * is self-contained and demonstrates core language features, patterns, and practical tips.
 *
 * NOTE: This is intentionally verbose so you can learn from the code and the comments.
 ***************************************************************************************************/

/* =======================================================================================
   0. Strict mode & top-level notes
   - 'use strict' enables safer semantics (throws on silent errors, forbids some legacy behavior).
   - JavaScript differs between environments (browser vs Node). When in doubt, test in target env.
   ======================================================================================= */
   'use strict';

   console.log('\n=== JavaScript: Intro & Types ===\n');
   
   /* =======================================================================================
      1. Primitives & typeof
      - JS has 7 primitive-ish types: undefined, null (special), boolean, number, bigint, string, symbol.
      - Everything else is an object (functions are callable objects).
      ======================================================================================= */
   const undef = undefined;
   const nul = null;
   const bool = true;
   const num = 42;
   const big = 123n; // BigInt literal (for very large integers)
   const str = "Hello, JS";
   const sym = Symbol('id');
   
   console.log(typeof undef, typeof nul, typeof bool, typeof num, typeof big, typeof str, typeof sym);
   // Output: "undefined object boolean number bigint string symbol"
   // Note: typeof null === 'object' is a historical quirk.
   
   /* =======================================================================================
      2. Variables: var, let, const, hoisting, TDZ (Temporal Dead Zone)
      - var: function-scoped, hoisted; avoid it.
      - let/const: block-scoped, not accessible before initialization (TDZ).
      - const: binding cannot be reassigned (object contents still mutable).
      ======================================================================================= */
   function scopeExample() {
     // var hoistedExample = undefined; (conceptually)
     if (true) {
       var v = 'var scope';
       let l = 'let scope';
       const c = 'const scope';
       console.log(v, l, c);
     }
     console.log(v); // OK (function-scoped)
     // console.log(l); // ReferenceError (TDZ)
   }
   scopeExample();
   
   /* =======================================================================================
      3. Functions — declaration, expression, arrow, this differences
      - Declarations are hoisted. Arrow functions don't have their own `this`.
      ======================================================================================= */
   function add(a = 0, b = 0) { return a + b; }            // declaration
   const mul = function(a, b) { return a * b; };           // expression
   const sq = x => x * x;                                  // arrow (concise)
   
   console.log(add(2,3), mul(4,5), sq(6));
   
   /* `this` example */
   const obj = {
     v: 10,
     method() { return this.v; },
     arrow: () => { /* arrow uses surrounding `this` (global/undefined) */ return this; }
   };
   console.log(obj.method()); // 10
   console.log(obj.arrow());  // in strict mode: undefined (in Node global is not `window`)
   
   /* =======================================================================================
      4. Objects & property patterns
      - dynamic keys, computed properties, getters/setters, property descriptors
      ======================================================================================= */
   const key = 'dynamic';
   const o = {
     id: 1,
     name: 'Alice',
     [key]: 123,         // computed property name
     get display() {     // getter
       return `${this.name}#${this.id}`;
     },
     set setName(val) {  // setter
       this.name = String(val);
     }
   };
   
   console.log(o.dynamic, o.display);
   o.setName = 'Bob';
   console.log(o.display);
   
   /* Object immutability helpers */
   const freezeExample = { a: 1 };
   Object.freeze(freezeExample);
   // freezeExample.a = 2; // silently fails in non-strict; throws in strict for some engines
   
   /* =======================================================================================
      5. Arrays and common methods
      - map, filter, reduce, find, some, every, forEach, flatMap
      ======================================================================================= */
   const arr = [1,2,3,4,5];
   console.log('map->squares', arr.map(x => x*x));
   console.log('filter->even', arr.filter(x => x%2 === 0));
   console.log('reduce->sum', arr.reduce((s,x) => s+x, 0));
   
   /* Avoid mutation when possible */
   const original = [1,2,3];
   const newArr = [...original, 4]; // spread to create new array
   console.log(original, newArr);
   
   /* =======================================================================================
      6. Destructuring, rest, spread
      - Clean unpacking of arrays/objects
      ======================================================================================= */
   const person = { name: 'Eve', age: 30, city: 'Dhaka' };
   const { name, age, ...rest } = person;
   console.log(name, age, rest); // rest contains { city: 'Dhaka' }
   
   /* =======================================================================================
      7. Template literals and tagged templates
      ======================================================================================= */
   const nameTpl = `User: ${person.name} (${person.age})`;
   console.log(nameTpl);
   
   /* =======================================================================================
      8. Equality: == vs ===
      - Use === (strict equality). == does coercion (surprising behavior).
      ======================================================================================= */
   console.log('0 == false', 0 == false, '0 === false', 0 === false);
   console.log('null == undefined', null == undefined, 'null === undefined', null === undefined);
   
   /* =======================================================================================
      9. Closures & module pattern
      ======================================================================================= */
   function counterFactory(init = 0) {
     let count = init;
     return {
       inc() { return ++count; },
       dec() { return --count; },
       get() { return count; }
     };
   }
   const counter = counterFactory(5);
   console.log(counter.inc(), counter.get());
   
   /* =======================================================================================
      10. Memoization example (closure + caching)
      ======================================================================================= */
   function memoize(fn) {
     const cache = new Map();
     return function(...args) {
       const key = JSON.stringify(args);
       if (cache.has(key)) return cache.get(key);
       const result = fn(...args);
       cache.set(key, result);
       return result;
     };
   }
   const fib = memoize(function(n) {
     if (n < 2) return n;
     return fib(n-1) + fib(n-2);
   });
   console.log('fib(20)=', fib(20));
   
   /* =======================================================================================
      11. Iterators & Generators
      - Generators produce lazily-evaluated sequences (yield)
      ======================================================================================= */
   function* idSequence() {
     let id = 1;
     while (true) yield id++;
   }
   const gen = idSequence();
   console.log(gen.next().value, gen.next().value);
   
   /* =======================================================================================
      12. Promises, microtasks, macrotasks, and async/await
      ======================================================================================= */
   console.log('\n--- Event loop demo (order matters) ---');
   setTimeout(() => console.log('macrotask: setTimeout 0'), 0);
   Promise.resolve().then(() => console.log('microtask: promise resolved'));
   console.log('sync: end of script line');
   
   /* Promises usage */
   const delay = ms => new Promise(res => setTimeout(res, ms));
   async function asyncFlow() {
     console.log('asyncFlow: start');
     await delay(50);
     console.log('asyncFlow: after 50ms');
   }
   asyncFlow();
   
   /* =======================================================================================
      13. Error handling & best practices
      - Prefer throwing Error objects, handle rejections, use try/catch in async functions
      ======================================================================================= */
   function parseJsonSafe(json) {
     try {
       return JSON.parse(json);
     } catch (err) {
       // Be explicit about error handling - don't swallow silently in real apps.
       console.error('JSON parse error:', err.message);
       return null;
     }
   }
   console.log(parseJsonSafe('{"ok":1}'), parseJsonSafe('not json'));
   
   /* =======================================================================================
      14. Advanced: Proxy, Reflect (meta-programming)
      - Useful for logging, validation, reactive frameworks
      ======================================================================================= */
   const target = { hello: 'world' };
   const proxy = new Proxy(target, {
     get(obj, prop) {
       console.log(`GET ${String(prop)}`);
       return Reflect.get(obj, prop);
     },
     set(obj, prop, val) {
       console.log(`SET ${String(prop)} = ${val}`);
       return Reflect.set(obj, prop, val);
     }
   });
   proxy.hello;
   proxy.a = 10;
   
   /* =======================================================================================
      15. Data structures: Map, Set, WeakMap, WeakSet
      - Prefer Map/Set when keys are not strings or when insertion order matters.
      ======================================================================================= */
   const map = new Map();
   map.set({id:1}, 'objKey'); // object keys allowed
   const set = new Set([1,2,3]);
   console.log(map.size, set.has(2));
   
   /* WeakMap for attaching metadata without preventing GC */
   const wm = new WeakMap();
   let objKey = {};
   wm.set(objKey, { meta: 'secret' });
   objKey = null; // eligible for GC eventually
   
   /* =======================================================================================
      16. Modules (ESM) & bundling notes
      - Use export/import in real apps. For Node: use .mjs or set "type":"module".
      - Keep modules small and focused (single responsibility).
      ======================================================================================= */
   
   /* =======================================================================================
      17. Patterns: Currying, Composition
      ======================================================================================= */
   const curry = fn => (...a) => a.length >= fn.length ? fn(...a) : (...b) => curry(fn)(...a, ...b);
   const add3 = (a,b,c) => a+b+c;
   const curriedAdd3 = curry(add3);
   console.log(curriedAdd3(1)(2)(3));
   
   const compose = (f,g) => x => f(g(x));
   const double = x => x*2;
   const plusOne = x => x+1;
   const doublePlusOne = compose(plusOne, double);
   console.log(doublePlusOne(3)); // plusOne(double(3)) = 7
   
   /* =======================================================================================
      18. Async patterns: concurrency control, Promise.all vs allSettled, throttling
      ======================================================================================= */
   async function fetchSimulated(id) {
     await delay(10 + Math.random()*40);
     if (Math.random() < 0.05) throw new Error('random failure');
     return { id, value: Math.random() };
   }
   async function fetchMany(ids) {
     // concurrency control: do not fire thousands at once
     const results = await Promise.allSettled(ids.map(fetchSimulated));
     return results.map(r => r.status === 'fulfilled' ? r.value : { error: r.reason.message });
   }
   fetchMany([1,2,3,4]).then(console.log);
   
   /* =======================================================================================
      19. Debounce and Throttle (useful for UI)
      ======================================================================================= */
   function debounce(fn, delayMs) {
     let timer = null;
     return function(...args) {
       clearTimeout(timer);
       timer = setTimeout(() => fn.apply(this, args), delayMs);
     };
   }
   function throttle(fn, intervalMs) {
     let last = 0;
     return function(...args) {
       const now = Date.now();
       if (now - last >= intervalMs) {
         last = now;
         fn.apply(this, args);
       }
     };
   }
   
   /* =======================================================================================
      20. Security reminders (web apps)
      - Never trust user input. Validate and sanitize server-side.
      - Avoid inline HTML insertion to prevent XSS; use templating or DOM APIs safely.
      - Use HTTPS and secure cookies; consider CSP and other headers.
      ======================================================================================= */
   
   /* =======================================================================================
      21. Performance & memory tips
      - Avoid creating large temporary arrays.
      - Prefer streaming for large data sets (Node streams).
      - Use WeakMap for caches with object keys to avoid memory leaks.
      - Profile with Node inspector / browser devtools.
      ======================================================================================= */
   
   /* =======================================================================================
      22. Testing & Debugging
      - Write unit tests with frameworks (Jest, Mocha).
      - Use console.log sparingly; prefer debuggers and structured logging.
      - Use source maps for transpiled code.
      ======================================================================================= */
   
   /* =======================================================================================
      23. Practical example: small in-memory "service" demonstrating many concepts
      - implements CRUD, validation, caching (simple), error handling, immutability
      ======================================================================================= */
   console.log('\n--- Practical in-memory service demo ---');
   
   const db = new Map(); // pretend DB
   let nextId = 1;
   
   function validateItem(data) {
     if (!data || typeof data.title !== 'string' || data.title.length === 0) {
       throw new Error('Invalid item: title required');
     }
   }
   
   function createItem(data) {
     validateItem(data);
     const item = { id: nextId++, title: data.title, created: Date.now() };
     db.set(item.id, item);
     return { ...item }; // return copy
   }
   
   function readItem(id) {
     const item = db.get(id);
     if (!item) throw new Error('Not found');
     return { ...item };
   }
   
   function updateItem(id, data) {
     validateItem(data);
     if (!db.has(id)) throw new Error('Not found');
     const updated = { ...db.get(id), title: data.title, updated: Date.now() };
     db.set(id, updated);
     return { ...updated };
   }
   function deleteItem(id) {
     return db.delete(id);
   }
   
   const it1 = createItem({ title: 'My item' });
   console.log('created', it1);
   console.log('read', readItem(it1.id));
   console.log('update', updateItem(it1.id, { title: 'My updated item' }));
   console.log('delete', deleteItem(it1.id), 'exists?', db.has(it1.id));
   
   /* =======================================================================================
      24. Advanced: Workers & multithreading (Node worker_threads, Web Workers)
      - Use workers for CPU-heavy tasks; avoid blocking the event loop.
      ======================================================================================= */
   /* Example note (not runnable here without creating a worker file):
      const { Worker } = require('worker_threads');
      const worker = new Worker('./heavyTask.js', { workerData: { ... } });
      worker.on('message', msg => { ... });
   */
   
   /* =======================================================================================
      25. Final advice & reading list
      - Read ECMAScript proposals and MDN docs for deep understanding.
      - Learn internals: how garbage collection works, how engines optimize code.
      - Practice building small apps and profiling them.
      ======================================================================================= */
   
   console.log('\n=== End of tutorial snippet ===\n');
   
   /***************************************************************************************************
    * If you'd like, I can:
    * - Produce a browser-friendly version with DOM examples and exercises.
    * - Split this giant file into "chapters" and create runnable tests/examples for each.
    * - Provide a downloadable PDF or GitHub repo structure with examples and exercises.
    ***************************************************************************************************/
   