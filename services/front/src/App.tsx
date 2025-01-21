import { Router, Route } from "@solidjs/router";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Redirect from "./pages/Redirect";
import NotFound from "./pages/NotFound";
import Layout from "./layouts/Nav";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
      <Router>
        <Route path="/login" component={Login} />
        <Route path="/redirect/:platform" component={Redirect} />
        <Route path="/" component={(props) => (
            <ProtectedRoute component={() => (<Layout>{props.children}</Layout>)} />
          )}
        >
          <Route path="/" component={Home} />
        </Route>
        <Route path="*404" component={NotFound} />
      </Router>
  );
}
