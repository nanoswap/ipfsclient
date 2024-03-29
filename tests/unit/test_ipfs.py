__package__ = "tests.unit"

import unittest
from typing import Self
from unittest.mock import MagicMock, patch
from multicodec import add_prefix

from ipfsclient.ipfs import Ipfs

import requests


class TestIpfs(unittest.TestCase):
    """Test the Ipfs Class."""

    @patch('ipfsclient.ipfs.requests.post')
    def test_dag_put(self: Self, mock_post: MagicMock) -> None:
        """Test the _dag_put function."""
        ipfs = Ipfs()

        # Mock the expected JSON response
        mock_response_content = '{"Cid": {"/": "some_cid_value"}}'
        mock_post.return_value.content.decode.return_value = \
            mock_response_content
        mock_post.return_value.raise_for_status.return_value = None

        # Call the function with sample data
        test_data = b"test data"
        cid = ipfs._dag_put(test_data)

        # Assertions
        assert cid == "some_cid_value"
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/dag/put",
            params={
                "store-codec": "raw",
                "input-codec": "raw"
            },
            files={
                "object data": add_prefix('raw', test_data)
            }
        )

    @patch('ipfsclient.ipfs.requests.post')
    def test_dag_get(self: Self, mock_post: MagicMock) -> None:
        """Test the _dag_get function."""
        ipfs = Ipfs()

        # Mock the expected JSON response
        mock_response_content = '{"key": "some_value"}'
        mock_post.return_value.content.decode.return_value = \
            mock_response_content
        mock_post.return_value.raise_for_status.return_value = None

        # Call the function with a sample filename
        test_filename = "test_file"
        response_data = ipfs._dag_get(test_filename)

        # Assertions
        assert response_data == {"key": "some_value"}
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/dag/get",
            params={
                "arg": test_filename,
            },
            files=None
        )

    @patch('ipfsclient.ipfs.requests.post')
    def test_mkdir(self: Self, mock_post: MagicMock) -> None:
        """Test the mkdir function."""
        ipfs = Ipfs()
        mock_post.return_value.raise_for_status.return_value = None
        ipfs.mkdir("test_dir")
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/files/mkdir",
            params={"arg": "/data/test_dir"},
            files=None
        )

    @patch('ipfsclient.ipfs.requests.post')
    def test_read(self: Self, mock_post: MagicMock) -> None:
        """Test the read function."""
        ipfs = Ipfs()
        mock_post.return_value.content = b"test data"
        result = ipfs.read("test_file")
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/files/read",
            params={"arg": "/data/test_file"},
            files=None
        )
        self.assertEqual(result, b"test data")

    @patch('ipfsclient.ipfs.requests.post')
    def test_add(self: Self, mock_post: MagicMock) -> None:
        """Test the add function."""
        ipfs = Ipfs()
        mock_post.return_value.content.decode.return_value = \
            '{"Hash": "some_hash_value"}'
        mock_post.return_value.raise_for_status.return_value = None
        ipfs.add("test_file", b"test data")
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/add",
            params={
                "to-files": "/data/test_file",
                "raw-leaves": True
            },
            files={
                "file": b"test data"
            }
        )

    @patch('ipfsclient.ipfs.requests.post')
    def test_does_file_exist_true(self: Self, mock_post: MagicMock) -> None:
        """Test with a file that does exist."""
        ipfs = Ipfs()
        mock_post.return_value.content = b"{}"
        result = ipfs.does_file_exist("test_file")
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/files/stat",
            params={"arg": "/data/test_file"},
            files=None
        )
        self.assertTrue(result)

    @patch('ipfsclient.ipfs.requests.post')
    def test_does_file_exist_false(self: Self, mock_post: MagicMock) -> None:
        """Test with a file that does not exist."""
        ipfs = Ipfs()
        mock_post.side_effect = requests.exceptions.HTTPError(
            "file does not exist",
            response=MagicMock(
                status_code=404,
                _content=b'file does not exist'
            )
        )
        result = ipfs.does_file_exist("test_file")
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/files/stat",
            params={"arg": "/data/test_file"},
            files=None
        )
        self.assertFalse(result)

    @patch('ipfsclient.ipfs.requests.post')
    def test_stat(self: Self, mock_post: MagicMock) -> None:
        """Test the stat function."""
        ipfs = Ipfs()
        mock_post.return_value.content = b'{"Type": 2, "CumulativeSize": 0, "Blocks": 0}'  # noqa: E501
        result = ipfs.stat("test_file")
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/files/stat",
            params={"arg": "/data/test_file"},
            files=None
        )
        self.assertEqual(result, {"Type": 2, "CumulativeSize": 0, "Blocks": 0})

    @patch('ipfsclient.ipfs.requests.post')
    def test_delete(self: Self, mock_post: MagicMock) -> None:
        """Test the delete function."""
        ipfs = Ipfs()
        # Call the function
        ipfs.delete("path/to/file.txt")

        # Assert that the correct params were passed to _make_request
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/files/rm",
            params={"arg": "/data/path/to/file.txt", "recursive": True},
            files=None
        )
