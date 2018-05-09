pf = (new yoob.Playfield()).init({defaultValue:defaultCell});
for (var i = 0; i < initialPlayfield.length; i++) {
  var t = initialPlayfield[i];
  pf.putDirty(t[0], t[1], t[2]);
}
pf.recalculateBounds();
newPf = (new yoob.Playfield()).init({defaultValue:defaultCell});
evolve_playfield(pf, newPf);
console.log('-----');
console.log(newPf.dump(dumpMapper).replace(/\n$/, ""));
console.log('-----');
