# SAM Online — virtual classroom site

A clean, responsive, static redesign of samonline.ca as a classroom / course
portal. No build step — just HTML, CSS, and a little vanilla JS.

## Files

```
index.html            # all page content & structure
assets/css/styles.css # all styling (theme tokens at the top)
assets/js/main.js      # footer year + mobile menu
```

## How to preview

Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000   # then visit http://localhost:8000
```

## How to edit (the common stuff)

- **Text & sections** — edit `index.html`. Sections are labelled with
  `<!-- ====== NAME ====== -->` comments (Hero, Courses, Features, Schedule,
  Resources, Login/Contact, Footer).
- **Colors / theme** — edit the CSS variables under `:root` at the top of
  `assets/css/styles.css`. Dark mode follows the system setting automatically.
- **Courses** — duplicate a `<article class="course-card">` block in
  `index.html` to add more.
- **Contact info** — update the email, phone, and address in the
  `#login` / `#contact` section and the footer.

All content is placeholder — swap it for the real classroom copy, links, and
class codes.

## Note

The live samonline.ca site couldn't be fetched from the build environment
(network egress blocked), so this is a fresh redesign based on a
"virtual classroom" brief rather than a 1:1 copy. Send the original HTML or a
screenshot to match it more closely.
