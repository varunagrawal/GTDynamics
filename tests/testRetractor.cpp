/* ----------------------------------------------------------------------------
 * GTDynamics Copyright 2020, Georgia Tech Research Corporation,
 * Atlanta, Georgia 30332-0415
 * All Rights Reserved
 * See LICENSE for the license information
 * -------------------------------------------------------------------------- */

/**
 * @file  testRetractor.cpp
 * @brief Test retractor for constraint manifold.
 * @author Yetong Zhang
 */

#include <CppUnitLite/TestHarness.h>
#include <gtdynamics/dynamics/DynamicsGraph.h>
#include <gtdynamics/optimizer/ConstraintManifold.h>
#include <gtdynamics/optimizer/Retractor.h>
#include <gtdynamics/universal_robot/RobotModels.h>
#include <gtdynamics/utils/Initializer.h>
#include <gtsam/base/Testable.h>
#include <gtsam/base/TestableAssertions.h>
#include <gtsam/base/numericalDerivative.h>
#include <gtsam/nonlinear/Expression.h>
#include <gtsam/slam/BetweenFactor.h>

#include <boost/format.hpp>

using namespace gtsam;
using namespace gtdynamics;

/** Simple example Pose3 with between constraints. */
TEST(TspaceBasis, connected_poses) {
  Key x1_key = 1;
  Key x2_key = 2;
  Key x3_key = 3;

  // Constraints.
  gtdynamics::EqualityConstraints constraints;
  auto noise = noiseModel::Unit::Create(6);
  auto factor12 = boost::make_shared<BetweenFactor<Pose3>>(
      x1_key, x2_key, Pose3(Rot3(), Point3(0, 0, 1)), noise);
  auto factor23 = boost::make_shared<BetweenFactor<Pose3>>(
      x2_key, x3_key, Pose3(Rot3(), Point3(0, 0, 1)), noise);
  constraints.emplace_shared<gtdynamics::FactorZeroErrorConstraint>(factor12);
  constraints.emplace_shared<gtdynamics::FactorZeroErrorConstraint>(factor23);

  // Create manifold values for testing.
  Values base_values;
  base_values.insert(x1_key, Pose3(Rot3(), Point3(0, 0, -1)));
  base_values.insert(x2_key, Pose3(Rot3(), Point3(0, 0, 1)));
  base_values.insert(x3_key, Pose3(Rot3(), Point3(0, 0, 3)));

  // Connected component.
  auto component = boost::make_shared<ConnectedComponent>(constraints);
  
  // Construct retractor.
  UoptRetractor retractor_uopt(component);
  ProjRetractor retractor_proj(component);
  KeyVector basis_keys{x3_key};
  BasisRetractor retractor_basis(component, basis_keys);

  Values values_uopt = retractor_uopt.retract(base_values);
  Values expected_uopt;
  expected_uopt.insert(x1_key, Pose3(Rot3(), Point3(0, 0, 0)));
  expected_uopt.insert(x2_key, Pose3(Rot3(), Point3(0, 0, 1)));
  expected_uopt.insert(x3_key, Pose3(Rot3(), Point3(0, 0, 2)));
  EXPECT(assert_equal(expected_uopt, values_uopt));

  Values values_proj = retractor_proj.retract(base_values);
  Values expected_proj;
  expected_proj.insert(x1_key, Pose3(Rot3(), Point3(0, 0, 0)));
  expected_proj.insert(x2_key, Pose3(Rot3(), Point3(0, 0, 1)));
  expected_proj.insert(x3_key, Pose3(Rot3(), Point3(0, 0, 2)));
  EXPECT(assert_equal(expected_proj, values_proj, 1e-4));

  Values values_basis = retractor_basis.retract(base_values); 
  Values expected_basis;
  expected_basis.insert(x1_key, Pose3(Rot3(), Point3(0, 0, 1)));
  expected_basis.insert(x2_key, Pose3(Rot3(), Point3(0, 0, 2)));
  expected_basis.insert(x3_key, Pose3(Rot3(), Point3(0, 0, 3)));
  EXPECT(assert_equal(expected_basis, values_basis));
}


int main() {
  TestResult tr;
  return TestRegistry::runAllTests(tr);
}
