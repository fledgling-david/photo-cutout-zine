# Generation Prompt and Quality Checklist

Use this reference after inspecting the user's photograph. First decide the theme word, poem copy, palette, and subject path; then fill the prompt. Do not pass unresolved placeholders to the image model.

## Photo-specific planning

Write a compact internal design brief containing:

- **Primary subject:** the one recognizable subject that should cross the typography.
- **Upward path:** the real part of the subject that can continue upward naturally (for example a head and shoulders, branch, flower stem, wing, raised arm, architectural edge, or reflection).
- **Scene anchor:** the visible lower-scene detail that keeps the subject connected to the photograph.
- **Preservation notes:** viewpoint, pose, proportions, relationships, and any details that must not change.
- **Theme word:** one short English word, ideally 3–7 letters, in uppercase.
- **Poem block A and B:** two original English fragments, each 1–2 short lines. Keep both brief and proofread them.
- **Ink palette:** one main ink color sampled conceptually from the photograph, plus a darker related color for small text. Do not use a fixed palette.
- **Halftone placement:** where the image is darkest and brightest, so the dot density can follow the photograph rather than cover it uniformly.
- **Thumbnail mode:** exact-overlay when the original file and script are available; otherwise model-rendered.

## Master prompt

Edit the attached photograph into ONE finished vertical 3:4 poetic retro editorial print poster. Use the attached photograph as the actual visual source, not merely as loose inspiration. The final result must be the complete poster artwork itself, flat and front-facing, with no product mockup, no room scene, no frame around the whole page, and no collage.

### Composition

Create one continuous image. The upper approximately one-third is quiet warm-white paper with generous negative space. It is not a separate rectangular panel. Keep the background, light, and photograph visually connected; do not introduce a hard horizontal split, straight cut line, rectangular pasted-on photo, cut-out halo, or abrupt gradient.

Place two brief English poetic text blocks in the upper paper area. Use a restrained small typewriter or monospaced face in a dark ink related to the photograph's palette. Keep them away from the top-right thumbnail reservation and away from the rising subject. Render the supplied wording exactly:

- Poem block A: [INSERT EXACT APPROVED WORDING]
- Poem block B: [INSERT EXACT APPROVED WORDING]

Across the middle, set this single theme word in huge uppercase high-contrast serif display letters, spanning most of the canvas width:

- Theme word: [INSERT ONE WORD]

The word must remain clearly readable. Let the real photographic subject overlap and hide only selected portions of a few letter strokes. The subject should rise naturally from the lower original scene, pass through the letterforms, and visibly extend above the top edge of the large word into the warm-white paper area. It must remain connected to the source scene, with realistic scale and perspective. Do not elongate the head or neck, stretch the body, change facial features or pose, invent a floating fragment, or detach the subject from its environment. Adjust the word position, size, or tracking before changing the subject.

### Color and print treatment

Choose the large word's ink color from a color that genuinely exists in the photograph: petals, fruit, foliage, walls, feathers, clothing, or water are possible sources. The color may be warm, cool, muted, saturated, or earthy depending on the source. Do not default to blue. Keep the large letters high-contrast against the photograph and paper.

Inside the photographic image and large letterforms, create a fine, clearly visible circular multicolor halftone print screen. Use cyan, magenta, and yellow ink dots, with optional black ink in the darkest areas. The color separations may be slightly misregistered, as in traditional color printing, but the offset must be subtle. Dots are small, round, and orderly enough to read as a real halftone screen. Make them denser in dark areas and more widely spaced in highlights. The halftone should be visibly present at normal viewing size, not merely a faint texture.

Do not substitute generic noise, film grain, scratches, paper speckles, or grunge for the halftone dots. Keep the upper warm-white paper comparatively clean. Preserve realistic photographic material and detail in the subject; the print treatment must not turn the subject into a flat illustration.

### Original thumbnail

Reserve the top-right corner for a small complete thumbnail of the original uploaded photograph, approximately 15–18% of the poster width. Maintain the source aspect ratio. Show the entire image without cropping, stretching, recoloring, retouching, or replacing any content. Add a fine border and the exact uppercase label ORIGINAL. Keep this inset clear of both poem blocks and the rising subject.

If thumbnail mode is exact-overlay, DO NOT draw any thumbnail or ORIGINAL label in the generated base image. Leave a clean, unobstructed reserved space at the top right; the exact original thumbnail and label will be added afterward by the local finishing script.

If thumbnail mode is model-rendered, render the actual attached photo as the inset. It must show the complete image and preserve its proportions. Do not invent a similar-looking replacement.

### Strict exclusions

No extra title, subtitle, date, location, credits, logo, watermark, unrelated decoration, additional object, or second image. Do not turn the result into a diptych or collage. Do not make a mockup. Do not use a fixed blue palette. Do not distort or replace the subject. Do not add ordinary noise or scratches in place of circular halftone dots.

### Output

Return exactly ONE finished vertical 3:4 poster. No contact sheet, no alternate versions, no side-by-side comparison, and no explanatory text baked into the artwork beyond the two supplied poem blocks, the one large theme word, and the required ORIGINAL label.

## Final quality checklist

Inspect the actual output at full size. Do not rely on the prompt alone.

1. **Format:** one image, portrait 3:4, complete edge-to-edge artwork.
2. **Continuity:** no visible horizontal panel seam, rectangular pasted photo, cut-out halo, or abrupt gradient.
3. **Subject:** recognizable and connected to the original scene; natural anatomy, scale, perspective, pose, and proportions.
4. **Typography:** exactly one large uppercase theme word; high-contrast serif; only partly occluded; still easy to read.
5. **Poetry:** exactly two short English blocks; correct spelling, grammar, and wording; small typewriter-style lettering; no accidental extra copy.
6. **Paper:** warm-white, relatively clean, with generous negative space.
7. **Color:** main word color is grounded in the source photograph and has readable contrast; no arbitrary default blue.
8. **Halftone:** clear circular cyan/magenta/yellow dots, subtle registration offset, dark-dense/light-sparse distribution; not generic noise.
9. **Photographic quality:** subject remains photographic, not plastic, vector-like, or over-smoothed.
10. **Thumbnail:** top right; full original image; aspect ratio preserved; fine border; label exactly ORIGINAL; no overlap with poems or subject.
11. **Exclusions:** no watermark, mockup, collage, extra title, date, or unrelated object.

If a check fails, identify the single most important defect and make a targeted correction. Preserve all successful parts. If exact thumbnail placement is required, use the finishing script and inspect the final PNG again.
