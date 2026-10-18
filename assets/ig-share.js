/* Instagram sharing. Instagram accepts nothing from a website: no link, no caption.
   On phones the page can hand the story's image to the phone's share sheet, where
   Instagram is listed (Feed, Stories, Messages); the caption and link are copied
   first so they can be pasted, the link into a Story link sticker.
   On computers there is no route into Instagram, so the caller keeps its fallback. */
(function () {
  var files = {};
  function phone() { return !!(window.matchMedia && window.matchMedia('(pointer: coarse)').matches); }
  function able() { return phone() && !!navigator.share && !!navigator.canShare; }
  function prepare(src) {
    if (!src || !able() || files[src] !== undefined) return;
    files[src] = null;
    fetch(src, { mode: 'cors' })
      .then(function (r) { return r.ok ? r.blob() : null; })
      .then(function (b) {
        if (!b) return;
        var f = new File([b], 'sircus-magazine.jpg', { type: b.type || 'image/jpeg' });
        if (navigator.canShare({ files: [f] })) files[src] = f;
      })
      .catch(function () {});
  }
  /* Returns true when the phone's share sheet was opened. Call it inside the click. */
  function share(src, title, text) {
    var f = files[src];
    if (!able() || !f) return false;
    navigator.share({ files: [f], title: title || 'SIRCUS Magazine', text: text || '' }).catch(function () {});
    return true;
  }
  window.sircusInstagram = { prepare: prepare, share: share, phone: phone };
})();
