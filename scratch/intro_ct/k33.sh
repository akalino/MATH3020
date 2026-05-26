for f in ./blender_json_exports/k33_leaf_collapse_step_*.json; do
  name=$(basename "$f" .json)
  blender --background --python render_in_blender.py -- \
    "$f" "./blender_outs/${name}.png"
done