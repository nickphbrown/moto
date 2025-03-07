import boto3
from botocore.exceptions import ClientError
import sure  # noqa # pylint: disable=unused-import
import pytest

from moto import mock_swf


# RegisterActivityType endpoint
@mock_swf
def test_register_activity_type_boto3():
    client = boto3.client("swf", region_name="us-west-2")
    client.register_domain(
        name="test-domain", workflowExecutionRetentionPeriodInDays="60"
    )
    client.register_activity_type(
        domain="test-domain", name="test-activity", version="v1.0"
    )

    types = client.list_activity_types(
        domain="test-domain", registrationStatus="REGISTERED"
    )["typeInfos"]
    types.should.have.length_of(1)
    actype = types[0]
    actype["activityType"]["name"].should.equal("test-activity")
    actype["activityType"]["version"].should.equal("v1.0")


@mock_swf
def test_register_already_existing_activity_type_boto3():
    client = boto3.client("swf", region_name="us-west-2")
    client.register_domain(
        name="test-domain", workflowExecutionRetentionPeriodInDays="60"
    )
    client.register_activity_type(
        domain="test-domain", name="test-activity", version="v1.0"
    )

    with pytest.raises(ClientError) as ex:
        client.register_activity_type(
            domain="test-domain", name="test-activity", version="v1.0"
        )
    ex.value.response["Error"]["Code"].should.equal("TypeAlreadyExistsFault")
    ex.value.response["Error"]["Message"].should.equal(
        "ActivityType=[name=test-activity, version=v1.0]"
    )
    ex.value.response["ResponseMetadata"]["HTTPStatusCode"].should.equal(400)


# ListActivityTypes endpoint


# ListActivityTypes endpoint
@mock_swf
def test_list_activity_types_boto3():
    client = boto3.client("swf", region_name="us-west-2")
    client.register_domain(
        name="test-domain", workflowExecutionRetentionPeriodInDays="60"
    )
    client.register_activity_type(
        domain="test-domain", name="b-test-activity", version="v1.0"
    )
    client.register_activity_type(
        domain="test-domain", name="a-test-activity", version="v1.0"
    )
    client.register_activity_type(
        domain="test-domain", name="c-test-activity", version="v1.0"
    )

    types = client.list_activity_types(
        domain="test-domain", registrationStatus="REGISTERED"
    )
    names = [
        activity_type["activityType"]["name"] for activity_type in types["typeInfos"]
    ]
    names.should.equal(["a-test-activity", "b-test-activity", "c-test-activity"])


@mock_swf
def test_list_activity_types_reverse_order_boto3():
    client = boto3.client("swf", region_name="us-west-2")
    client.register_domain(
        name="test-domain", workflowExecutionRetentionPeriodInDays="60"
    )
    client.register_activity_type(
        domain="test-domain", name="b-test-activity", version="v1.0"
    )
    client.register_activity_type(
        domain="test-domain", name="a-test-activity", version="v1.0"
    )
    client.register_activity_type(
        domain="test-domain", name="c-test-activity", version="v1.0"
    )

    types = client.list_activity_types(
        domain="test-domain", registrationStatus="REGISTERED", reverseOrder=True
    )

    names = [
        activity_type["activityType"]["name"] for activity_type in types["typeInfos"]
    ]
    names.should.equal(["c-test-activity", "b-test-activity", "a-test-activity"])


# DeprecateActivityType endpoint
@mock_swf
def test_deprecate_activity_type_boto3():
    client = boto3.client("swf", region_name="us-west-2")
    client.register_domain(
        name="test-domain", workflowExecutionRetentionPeriodInDays="60"
    )
    client.register_activity_type(
        domain="test-domain", name="test-activity", version="v1.0"
    )
    client.deprecate_activity_type(
        domain="test-domain", activityType={"name": "test-activity", "version": "v1.0"}
    )

    types = client.list_activity_types(
        domain="test-domain", registrationStatus="DEPRECATED"
    )
    types.should.have.key("typeInfos").being.length_of(1)
    actype = types["typeInfos"][0]
    actype["activityType"]["name"].should.equal("test-activity")
    actype["activityType"]["version"].should.equal("v1.0")


@mock_swf
def test_deprecate_already_deprecated_activity_type_boto3():
    client = boto3.client("swf", region_name="us-west-2")
    client.register_domain(
        name="test-domain", workflowExecutionRetentionPeriodInDays="60"
    )
    client.register_activity_type(
        domain="test-domain", name="test-activity", version="v1.0"
    )
    client.deprecate_activity_type(
        domain="test-domain", activityType={"name": "test-activity", "version": "v1.0"}
    )

    with pytest.raises(ClientError) as ex:
        client.deprecate_activity_type(
            domain="test-domain",
            activityType={"name": "test-activity", "version": "v1.0"},
        )
    ex.value.response["Error"]["Code"].should.equal("TypeDeprecatedFault")
    ex.value.response["Error"]["Message"].should.equal(
        "ActivityType=[name=test-activity, version=v1.0]"
    )
    ex.value.response["ResponseMetadata"]["HTTPStatusCode"].should.equal(400)


@mock_swf
def test_deprecate_non_existent_activity_type_boto3():
    client = boto3.client("swf", region_name="us-west-2")
    client.register_domain(
        name="test-domain", workflowExecutionRetentionPeriodInDays="60"
    )

    with pytest.raises(ClientError) as ex:
        client.deprecate_activity_type(
            domain="test-domain",
            activityType={"name": "test-activity", "version": "v1.0"},
        )
    ex.value.response["Error"]["Code"].should.equal("UnknownResourceFault")
    ex.value.response["Error"]["Message"].should.equal(
        "Unknown type: ActivityType=[name=test-activity, version=v1.0]"
    )
    ex.value.response["ResponseMetadata"]["HTTPStatusCode"].should.equal(400)


# DeprecateActivityType endpoint
@mock_swf
def test_undeprecate_activity_type():
    client = boto3.client("swf", region_name="us-east-1")
    client.register_domain(
        name="test-domain", workflowExecutionRetentionPeriodInDays="60"
    )
    client.register_activity_type(
        domain="test-domain", name="test-activity", version="v1.0"
    )
    client.deprecate_activity_type(
        domain="test-domain", activityType={"name": "test-activity", "version": "v1.0"}
    )
    client.undeprecate_activity_type(
        domain="test-domain", activityType={"name": "test-activity", "version": "v1.0"}
    )

    resp = client.describe_activity_type(
        domain="test-domain", activityType={"name": "test-activity", "version": "v1.0"}
    )
    resp["typeInfo"]["status"].should.equal("REGISTERED")


@mock_swf
def test_undeprecate_already_undeprecated_activity_type():
    client = boto3.client("swf", region_name="us-east-1")
    client.register_domain(
        name="test-domain", workflowExecutionRetentionPeriodInDays="60"
    )
    client.register_activity_type(
        domain="test-domain", name="test-activity", version="v1.0"
    )
    client.deprecate_activity_type(
        domain="test-domain", activityType={"name": "test-activity", "version": "v1.0"}
    )
    client.undeprecate_activity_type(
        domain="test-domain", activityType={"name": "test-activity", "version": "v1.0"}
    )

    client.undeprecate_activity_type.when.called_with(
        domain="test-domain", activityType={"name": "test-activity", "version": "v1.0"}
    ).should.throw(ClientError)


@mock_swf
def test_undeprecate_never_deprecated_activity_type():
    client = boto3.client("swf", region_name="us-east-1")
    client.register_domain(
        name="test-domain", workflowExecutionRetentionPeriodInDays="60"
    )
    client.register_activity_type(
        domain="test-domain", name="test-activity", version="v1.0"
    )

    client.undeprecate_activity_type.when.called_with(
        domain="test-domain", activityType={"name": "test-activity", "version": "v1.0"}
    ).should.throw(ClientError)


@mock_swf
def test_undeprecate_non_existent_activity_type():
    client = boto3.client("swf", region_name="us-east-1")
    client.register_domain(
        name="test-domain", workflowExecutionRetentionPeriodInDays="60"
    )

    client.undeprecate_activity_type.when.called_with(
        domain="test-domain", activityType={"name": "test-activity", "version": "v1.0"}
    ).should.throw(ClientError)


# DescribeActivityType endpoint
@mock_swf
def test_describe_activity_type_boto3():
    client = boto3.client("swf", region_name="us-east-1")
    client.register_domain(
        name="test-domain", workflowExecutionRetentionPeriodInDays="60"
    )
    client.register_activity_type(
        domain="test-domain",
        name="test-activity",
        version="v1.0",
        defaultTaskList={"name": "foo"},
        defaultTaskHeartbeatTimeout="32",
    )

    actype = client.describe_activity_type(
        domain="test-domain", activityType={"name": "test-activity", "version": "v1.0"}
    )
    actype["configuration"]["defaultTaskList"]["name"].should.equal("foo")
    infos = actype["typeInfo"]
    infos["activityType"]["name"].should.equal("test-activity")
    infos["activityType"]["version"].should.equal("v1.0")
    infos["status"].should.equal("REGISTERED")


@mock_swf
def test_describe_non_existent_activity_type_boto3():
    client = boto3.client("swf", region_name="us-east-1")
    client.register_domain(
        name="test-domain", workflowExecutionRetentionPeriodInDays="60"
    )

    with pytest.raises(ClientError) as ex:
        client.describe_activity_type(
            domain="test-domain",
            activityType={"name": "test-activity", "version": "v1.0"},
        )
    ex.value.response["Error"]["Code"].should.equal("UnknownResourceFault")
    ex.value.response["Error"]["Message"].should.equal(
        "Unknown type: ActivityType=[name=test-activity, version=v1.0]"
    )
    ex.value.response["ResponseMetadata"]["HTTPStatusCode"].should.equal(400)
