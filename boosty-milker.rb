class BoostyMilker < Formula
  include Language::Python::Virtualenv

  desc "CLI tool to download photos from Boosty"
  homepage "https://github.com/F3T1W/BoostyMilker"
  url "https://github.com/F3T1W/BoostyMilker/archive/refs/tags/v1.0.3.tar.gz"
  sha256 "2ea00627a3add0712effa3c12a1f225708ac1435f186e95f28020c7fe04a3203"
  license "MIT"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/boosty-milker", "--help"
  end
end
