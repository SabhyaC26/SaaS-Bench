# Batch Schema Design Process

This document describes the recommended approach: **analyze all tutorials upfront, then build one comprehensive schema**.

## Why This Approach?

Instead of extending the schema incrementally as tutorials are discovered, it's more efficient to:

1. **Process all tutorials at once** - Get complete picture of resource types needed
2. **Analyze comprehensively** - Identify all properties and relationships
3. **Build complete schema** - Design once with all requirements
4. **Avoid refactoring** - No need to extend schema multiple times

## Process

### Step 1: Collect Tutorial URLs

Create a file with all tutorial URLs you want to process:

```bash
cat > tutorials.txt << EOF
https://docs.databricks.com/aws/en/getting-started/create-table
https://docs.databricks.com/aws/en/getting-started/quick-start
https://docs.databricks.com/aws/en/catalogs/create-catalog
https://docs.databricks.com/aws/en/schemas/create-schema
# ... add more URLs
EOF
```

### Step 2: Batch Process All Tutorials

Run the batch analysis script:

```bash
python scripts/analyze_tutorials_batch.py \
  $(cat tutorials.txt) \
  --analysis-output tutorial_analysis.json \
  --recommendations-output schema_recommendations.md
```

This will:
- Process all tutorials
- Extract workflows to YAML
- Analyze resource types and properties
- Generate recommendations for schema design

### Step 3: Review Analysis Results

Check the generated files:

1. **`tutorial_analysis.json`**: Complete analysis with:
   - All workflows processed
   - Resource types found
   - Properties for each resource type
   - Tools used
   - Errors (if any)

2. **`schema_recommendations.md`**: Recommendations including:
   - New resource types needed
   - Missing tools
   - Properties to include

### Step 4: Design Comprehensive Schema

Based on the analysis, design the complete schema:

1. **Add all resource types** to `state.py`
2. **Add all properties** discovered from tutorials
3. **Create all API tools** in `tools.py`
4. **Register all tools** in `registry.py`
5. **Update evaluation** to handle all resource types
6. **Add policy validation** for all resources

### Step 5: Validate Against All Tutorials

Once the schema is built:

```bash
# Validate all workflows
python scripts/validate_workflows.py

# Run tests
pytest

# Test with actual workflows
python scripts/test_workflow_execution.py workflows/databricks/*.yaml
```

## Example Workflow

```bash
# 1. List all tutorial URLs
TUTORIALS=(
  "https://docs.databricks.com/aws/en/getting-started/create-table"
  "https://docs.databricks.com/aws/en/getting-started/quick-start"
  "https://docs.databricks.com/aws/en/catalogs/create-catalog"
  # ... 7 more
)

# 2. Process all at once
python scripts/analyze_tutorials_batch.py "${TUTORIALS[@]}"

# 3. Review recommendations
cat schema_recommendations.md

# 4. Build comprehensive schema based on analysis
# (Follow SCHEMA_EXTENSION_GUIDE.md but do it all at once)

# 5. Validate
python scripts/validate_workflows.py
pytest
```

## Benefits

✅ **One-time design** - Build schema once with all requirements
✅ **Complete coverage** - All resource types identified upfront
✅ **No refactoring** - Avoids multiple schema extensions
✅ **Better testing** - Can test against all tutorials immediately
✅ **Clear requirements** - Analysis shows exactly what's needed

## Comparison

### Incremental Approach (Old)
```
Tutorial 1 → Extend schema → Tutorial 2 → Extend schema → ...
```

### Batch Approach (Recommended)
```
All Tutorials → Analyze → Design Complete Schema → Validate
```

## Next Steps

1. Provide your 10 tutorial URLs
2. Run batch analysis
3. Review recommendations
4. Build comprehensive schema
5. Validate against all tutorials

