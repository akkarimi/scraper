<View>
  <Image name="img" value="$image"></Image>
  <Header name="label_cat" value="Category"></Header>
  <Labels name="category" toName="text">
    <Label alias="D" value="design"/>
    <Label alias="C" value="color"/>
    <Label alias="P" value="price"/>
    <Label alias="G" value="garment part"/>
    <Label alias="Q" value="quality"/>
    <Label alias="O" value="other"/>
  </Labels>
  <Header name="label_pol" value="Polarity"></Header>
  <Labels name="polarity" toName="text">
    <Label alias="p" value="positive" background="green"/>
    <Label alias="ne" value="negative" background="red"/>
    <Label alias="nl" value="neutral" background="gray"/>
    <Label alias="u" value="unknown" background="black"/>
  </Labels>
  <Text name="text" value="$text"/>
</View>
