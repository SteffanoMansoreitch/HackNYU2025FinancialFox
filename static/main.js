import express from "express";
import bodyparser from "body-parser";

const app = express();
const port = 3000;

app.set("view engine", "ejs"); // ✅ Set EJS as the view engine
app.use(express.static("public")); // ✅ Serve static files like CSS and JS
app.use(bodyparser.urlencoded({ extended: true }));

const data = {
  name: "Your name",
  entertainment: 200,
  entertainmentPercentage: 15,
  utilities: 50,
  utilitiesPercentage: 5,
  healthcare: 100,
  healthcarePercentage: 7,
  transport: 300,
  transportPercentage: 22,
  food: 100,
  foodPercentage: 7,
  rent: 500,
  rentPercentage: 37,
  misc: 100,
  miscPercentage: 7,
  total: 1350,
  savings: 180,
};

function updateSprite(savings) {
  if (savings < 150) return "260px -90px";
  else if (savings < 300) return "-88px -90px";
  else return "530px -450px";
}

app.get("/", (req, res) => {
  const spritePosition = updateSprite(data.savings);
  res.render("index", { data: data, spritePosition: spritePosition }); // ✅ No need to add `.ejs`
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
